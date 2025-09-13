from django.views import View
from assignments.models import Task
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import TemplateView
from .forms import StudentSignupForm
class ChooseRoleView(View):
    template_name = "accounts/role_select.html"
    roles = ["student", "admin"]

    # mode = "login" or "signup"
    mode = None  
    ROLE_MAP = {
        "signup": ["student"],
        "login": ["student", "admin"]
    }

    def get(self, request):
        roles = self.ROLE_MAP.get(self.mode, [])


        
        
        return render(request, self.template_name, {
            "roles": roles,
 
            "page_type": self.mode
        })

    def post(self, request):
        role = request.POST.get("role")
        print("role_sect",request.POST.get("role"))
        if role not in self.roles:
            return redirect(request.path)  # just reload same page

        request.session["selected_role"] = role

   
        if self.mode == "login":
            return redirect("login")

        elif self.mode == "signup":
            if role == "student":
                return redirect("student_signup")
            elif role == "teacher":
                return redirect("teacher_signup")
            


        return redirect(request.path)  # fallback
    

class ChooseRoleLoginView(ChooseRoleView):
    mode = "login"

class ChooseRoleSignupView(ChooseRoleView):
    mode = "signup"




class CustomLoginView(LoginView):
    template_name = "accounts/login.html"   # create this template
    redirect_authenticated_user = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        selected_role = self.request.session.get("selected_role")
        if selected_role:  # only set if chosen earlier
            context["role"] = selected_role
        return context

    def get_success_url(self):
        """Redirect user to correct dashboard after login"""
        user = self.request.user
        if user.role == "student":
            return reverse_lazy("task_list")
        elif user.role == "teacher":
            return reverse_lazy("teacher_dashboard")
        return reverse_lazy("home")  # fallback

    def form_valid(self, form):
        """Check that the role chosen matches the user's actual role"""
        selected_role = self.request.session.get("selected_role")
        user = form.get_user()

        if selected_role and user.role != selected_role:
            messages.error(self.request, "You selected the wrong role. Please try again.")
            return redirect("choose-role-login")

        return super().form_valid(form)
    

class StudentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/student_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Student Dashboard"
        # later you can add student-specific data here
        return context




class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Admin Dashboard"

        # Status-based tasks
        context["pending_tasks"] = Task.objects.filter(status="pending", is_deleted=False)
        context["approved_tasks"] = Task.objects.filter(status="approved", is_deleted=False)
        context["rejected_tasks"] = Task.objects.filter(status="rejected", is_deleted=False)

        # Counts
        context["pending_count"] = context["pending_tasks"].count()
        context["approved_count"] = context["approved_tasks"].count()
        context["rejected_count"] = context["rejected_tasks"].count()

        # Total tasks
        context["total_count"] = Task.objects.filter(is_deleted=False).count()

        # Recent tasks (last 5)
        context["recent_tasks"] = Task.objects.filter(is_deleted=False).order_by("-created_at")[:5]

        return context


class StudentSignupView(View):
    template_name = "accounts/student_signup.html"

    def get(self, request):
        form = StudentSignupForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = StudentSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")  # redirect to login page after signup
        return render(request, self.template_name, {"form": form})