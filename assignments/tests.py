# assignments/models.py
from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField()
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,      # if user is deleted, keep task but set null
        related_name="tasks",
        null=True,                      # allow null in DB
        blank=True                      # allow empty in forms
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
