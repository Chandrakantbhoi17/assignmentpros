from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'due_date', 'assigned_to', 'created_by', 'is_deleted')
    list_filter = ('status', 'is_deleted', 'due_date')
    search_fields = ('title', 'description', 'assigned_to__username', 'created_by__username')
    ordering = ('-created_at',)

    # Optional: Readonly fields
    readonly_fields = ('created_at',)

    # Optional: Customize how fields are grouped in the admin form
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'due_date', 'status', 'assigned_to', 'file', 'created_by', 'is_deleted')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
