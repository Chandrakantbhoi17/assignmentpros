# assignments/views.py
import os
import razorpay
import json
import hashlib
import hmac
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView,CreateView,View,DetailView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task, TaskPayment
from .forms import StudentTaskForm,TaskUpdateForm
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from assignments.models import Task
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone

from django.shortcuts import redirect, get_object_or_404

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"
    paginate_by = 5
    template_name = "assignments/task_list.html"

    def get_queryset(self):
        """Admins see all tasks, students only see their own tasks."""
        user = self.request.user

        # Admins see everything (excluding soft-deleted)
        if user.role == "admin":
            return Task.objects.filter(is_deleted=False).order_by("-created_at")

        # Students see only their own created tasks
        if user.role == "student":
            return Task.objects.filter(
                created_by=user,
                is_deleted=False
            ).order_by("-created_at")

        # Fallback: no tasks
        return Task.objects.none()

        

class StudentTaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = StudentTaskForm
    template_name = "assignments/add_task.html"
    success_url = reverse_lazy('task_list')  # redirect after successful submission

    def form_valid(self, form):
        # Automatically set the logged-in user as creator
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        """Include file data when form is submitted"""
        kwargs = super().get_form_kwargs()
        if self.request.method in ("POST", "PUT"):
            kwargs.update({"files": self.request.FILES})
        return kwargs


class TaskDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        user = request.user

        if user.role == "admin":
            # Admins can delete any task
            task = get_object_or_404(Task, pk=pk, is_deleted=False)
        else:
            # Students can only delete their own tasks
            task = get_object_or_404(Task, pk=pk, created_by=user, is_deleted=False)

        task.is_deleted = True
        task.save()

        if user.role == "student":
            return redirect("task_list")
        elif user.role == "admin":
            return redirect("admin_task_list")
        


class TaskFileDownloadView(LoginRequiredMixin, View):

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        user = request.user

        # ✅ Permission check
        if not (
            user.is_superuser or
            getattr(user, 'role', '') == 'admin' or
            user == task.created_by or
            user == task.assigned_to
        ):
            return HttpResponse("Unauthorized", status=401)

        # ✅ Check if file exists
        if not task.file or not os.path.exists(task.file.path):
            raise Http404("File not found.")

        # ✅ Return file as download
        return FileResponse(
            open(task.file.path, 'rb'),
            as_attachment=True,
            filename=os.path.basename(task.file.name)
        )
class TaskCompletedFileDownloadView(LoginRequiredMixin, View):

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        user = request.user

        # Permission check — same as doubt file:
        if not (
            user.is_superuser or
            getattr(user, 'role', '') == 'admin' or
            user == task.created_by or
            user == task.assigned_to
        ):
            return HttpResponse("Unauthorized", status=401)

        # Check if completed_file exists
        if not task.completed_file or not os.path.exists(task.completed_file.path):
            raise Http404("File not found.")

        # Return file as attachment for download
        return FileResponse(
            open(task.completed_file.path, 'rb'),
            as_attachment=True,
            filename=os.path.basename(task.completed_file.name)
        )
class TaskDetailView(LoginRequiredMixin,DetailView):
    model = Task
    template_name = 'assignments/task_view.html'
    context_object_name = 'task'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['razorpay_key_id'] = settings.RAZORPAY_KEY_ID
        
        # Add payment information for students
        if self.request.user.role == 'student':
            task = self.get_object()
            context['first_half_paid'] = TaskPayment.objects.filter(
                task=task,
                student=self.request.user,
                type='first_half',
                status='completed'
            ).exists()
            context['second_half_paid'] = TaskPayment.objects.filter(
                task=task,
                student=self.request.user,
                type='second_half',
                status='completed'
            ).exists()
        
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        if request.user.role == 'admin':
            if 'amount' in request.POST:
                amount = request.POST.get('amount')
                task.amount = amount
                task.save()
            elif 'action' in request.POST:
                action = request.POST.get('action')
                if action == 'approve':
                    task.status = 'approved'
                    task.save()
                elif action == 'reject':
                    task.status = 'rejected'
                    task.save()
        return redirect('task_detail', pk=task.pk)
        

class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskUpdateForm
    template_name = 'assignments/task_form.html'
    success_url = '/tasks/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass user to the form
        return kwargs

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user, 'role', '') == 'admin':
            return Task.objects.all()
        return Task.objects.filter(created_by=user) | Task.objects.filter(assigned_to=user)
    def get_success_url(self):
        # Option 1: Redirect to task detail page
        return reverse('task_detail', kwargs={'pk': self.object.pk})


@method_decorator(csrf_exempt, name='dispatch')
class CreateRazorpayOrderView(LoginRequiredMixin, View):
    """Create Razorpay order for task payment"""
    
    def post(self, request):
        try:
            task_id = request.POST.get('task_id')
            payment_phase = request.POST.get('payment_phase')
            
            if not task_id or not payment_phase:
                return JsonResponse({'error': 'Missing required parameters'}, status=400)
            
            task = get_object_or_404(Task, pk=task_id)
            
            # Check if user is authorized to make payment
            if request.user != task.created_by or request.user.role != 'student':
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            # Check if payment already exists for this phase
            existing_payment = TaskPayment.objects.filter(
                task=task,
                student=request.user,
                type=payment_phase
            ).exists()
            
            if existing_payment:
                return JsonResponse({'error': 'Payment already made for this phase'}, status=400)
            
            # Calculate amount (half of total task amount)
            amount = float(task.amount) / 2
            amount_in_paise = int(amount * 100)  # Convert to paise
            
            # Create Razorpay order
            order_data = {
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': f'task_{task_id}_{payment_phase}',
                'notes': {
                    'task_id': task_id,
                    'payment_phase': payment_phase,
                    'student_id': request.user.id
                }
            }
            
            order = razorpay_client.order.create(data=order_data)
            
            return JsonResponse({
                'order_id': order['id'],
                'amount': amount_in_paise,
                'currency': 'INR',
                'merchant_key': settings.RAZORPAY_KEY_ID,
                'task_id': task_id,
                'payment_phase': payment_phase
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessView(LoginRequiredMixin, View):
    """Handle successful payment verification"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            payment_id = data.get('payment_id')
            order_id = data.get('order_id')
            signature = data.get('signature')
            task_id = data.get('task_id')
            payment_phase = data.get('payment_phase')
            
            if not all([payment_id, order_id, signature, task_id, payment_phase]):
                return JsonResponse({'success': False, 'error': 'Missing required parameters'}, status=400)
            
            task = get_object_or_404(Task, pk=task_id)
            
            # Verify payment signature
            payment_data = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            try:
                razorpay_client.utility.verify_payment_signature(payment_data)
            except Exception as e:
                return JsonResponse({'success': False, 'error': 'Payment verification failed'}, status=400)
            
            # Get payment details from Razorpay
            payment_details = razorpay_client.payment.fetch(payment_id)
            
            # Create TaskPayment record
            amount_paid = float(payment_details['amount']) / 100  # Convert from paise to rupees
            
            task_payment = TaskPayment.objects.create(
                task=task,
                student=request.user,
                type=payment_phase,
                amount_paid=amount_paid,
                status='completed',
                transaction_id=payment_id,
                paid_at=timezone.now()
            )
            
            # Check if both payments are completed
            completed_payments = TaskPayment.objects.filter(
                task=task,
                student=request.user,
                status='completed'
            ).count()
            
            if completed_payments >= 2:  # Both first and second half paid
                task.is_paid = True
                task.save()
            
            return JsonResponse({'success': True, 'message': 'Payment successful'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)