from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from decimal import Decimal
import razorpay

from django.shortcuts import get_object_or_404

from assignments.models import  Task,TaskPayment

class HomeView(TemplateView):
    """
    Landing page view with Bootstrap navbar and welcome message.
    """
    template_name = "core/home.html"


class PrivacyPolicyView(TemplateView):
    """
    Privacy Policy page view.
    """
    template_name = "core/privacy_policy.html"


class ContactUsView(TemplateView):
    """
    Contact Us page view.
    """
    template_name = "core/contact_us.html"


class TermsAndConditionsView(TemplateView):
    """
    Terms & Conditions page view.
    """
    template_name = "core/terms_and_conditions.html"


class ShippingPolicyView(TemplateView):
    """
    Shipping Policy page view.
    """
    template_name = "core/shipping_policy.html"



class CancellationRefundsView(TemplateView):
    """
    Cancellation & Refunds page view.
    """
    template_name = "core/cancellation_refunds.html"




@method_decorator(csrf_exempt, name='dispatch')
class RazorpayOrderCreateView(View):
    def post(self, request, *args, **kwargs):
        try:
            task_id = request.POST.get('task_id')
            task = Task.objects.get(pk=task_id)
     
            # Check existing payments
            first_paid = TaskPayment.objects.filter(task=task, type='first_half', status='completed').exists()
            second_paid = TaskPayment.objects.filter(task=task,type='second_half', status='completed').exists()

            if first_paid and second_paid:
                return JsonResponse({'error': 'Both payments already completed'}, status=400)

            payment_phase = 'first_half' if not first_paid else 'second_half'
            amount_to_pay = task.amount / Decimal('2')

            # Create Razorpay Order
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            razorpay_order = client.order.create({
                "amount": int(amount_to_pay * 100),  # in paisa
                "currency": "INR",
                "payment_capture": 1
            })

            return JsonResponse({
                'order_id': razorpay_order['id'],
                'amount': int(amount_to_pay * 100),
                'currency': "INR",
                'merchant_key': settings.RAZORPAY_KEY_ID,
                'payment_phase': payment_phase,
                'task_id': task.pk,
         
            })

        except Task.DoesNotExist:
            return JsonResponse({'error': 'Task not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

@method_decorator(csrf_exempt, name='dispatch')
class RazorpayPaymentVerificationView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        import json

        try:
            data = json.loads(request.body)
            payment_id = data.get("payment_id")
            order_id = data.get("order_id")
            task_id = data.get("task_id")

            if not (payment_id and order_id and task_id):
                return JsonResponse({"error": "Invalid data received"}, status=400)

            task = get_object_or_404(Task, pk=task_id)

            # Optionally verify with Razorpay API
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            payment = client.payment.fetch(payment_id)

            if payment['status'] == 'captured':
                task.is_paid = True
                task.save()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"error": "Payment not captured"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)