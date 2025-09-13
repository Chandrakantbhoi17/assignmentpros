# assignments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("student/tasks", views.TaskListView.as_view(), name="task_list"),
    path("my/tasks", views.TaskListView.as_view(), name="admin_task_list"),
    path('student/task/add',views.StudentTaskCreateView.as_view(), name='student_task_add'),
    path('tasks/<int:pk>/delete',views.TaskDeleteView.as_view(), name='task_delete'),
    path('tasks/<int:pk>/download/',views.TaskFileDownloadView.as_view(), name='task_file_download'),
    path('tasks/<int:pk>/completed-file-download/',views.TaskCompletedFileDownloadView.as_view(), name='task_completed_file_download'),
    path('tasks/<int:pk>/',views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    
    # Razorpay payment URLs
    path('create-razorpay-order', views.CreateRazorpayOrderView.as_view(), name='create_razorpay_order'),
    path('payment-success', views.PaymentSuccessView.as_view(), name='payment_success'),
 
]
