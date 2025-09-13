import os
import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from assignmentpros.storage_backend import protected_storage


# --- Validators ---

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.docx', '.jpg', '.png']
    if ext not in valid_extensions:
        raise ValidationError('Unsupported file extension.')


def validate_file_size(value):
    max_size = 5 * 1024 * 1024  # 5 MB
    if value.size > max_size:
        raise ValidationError("File size exceeds 5MB.")


# --- File rename function ---

def task_file_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return new_filename


# --- Task Model ---

class Task(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # total cos
    is_deleted = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="tasks",
        null=True,
        blank=True
    )


    file = models.FileField(
        upload_to=task_file_upload_path,
        storage=protected_storage,
        validators=[validate_file_extension, validate_file_size],
        blank=True,
        null=True
    )

    completed_file = models.FileField(
        upload_to=task_file_upload_path,
        storage=protected_storage,
        validators=[validate_file_extension, validate_file_size],
        blank=True,
        null=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class TaskPayment(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('first_half', 'First Half'),
        ('second_half', 'Second Half'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    task = models.ForeignKey(
        'Task',
        on_delete=models.CASCADE,
        related_name='payments'
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='task_payments'
    )

    type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES
    )

    amount_paid = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'student', 'type')  # Prevent paying twice for same half

    def __str__(self):
        return f"{self.student.username} - {self.task.title} - {self.type} - {self.status}"