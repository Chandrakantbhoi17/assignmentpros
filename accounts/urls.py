from django.urls import path
from .views import (
    ChooseRoleLoginView,
    ChooseRoleSignupView,
    CustomLoginView,
    StudentDashboardView,
    AdminDashboardView,
    StudentSignupView
)
from django.contrib.auth import views as auth_views
urlpatterns = [
    # role selection
    path("choose-role/login", ChooseRoleLoginView.as_view(), name="choose-role-login"),
    path("choose-role/signup", ChooseRoleSignupView.as_view(), name="choose-role-signup"),

    # login
    path("login", CustomLoginView.as_view(), name="login"),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    

    # dashboards
    path("student/dashboard", StudentDashboardView.as_view(), name="student_dashboard"),
    path("adminn/dashboard", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("student/signup", StudentSignupView.as_view(), name="student_signup"),
]
