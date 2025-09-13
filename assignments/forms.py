from django import forms
from .models import Task

class StudentTaskForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'Optional description', 'rows': 3}
        )
    )

    file = forms.FileField(   # <-- added file field
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control'}
        )
    )

    class Meta:
        model = Task
        fields = ['title', 'due_date', 'description', 'file']  # <-- include file
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter task title'}),
        }
class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'due_date',
            'assigned_to',
            'status',
            'amount',
            'completed_file',
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Save user for clean validation
        self.initial['user'] = user

        # Restrict fields for non-admins
        if not (user and (user.is_superuser or getattr(user, 'role', '') == 'admin')):
            self.fields['assigned_to'].disabled = True
            self.fields['status'].disabled = True
            self.fields['completed_file'].widget = forms.HiddenInput()

    def clean_completed_file(self):
        user = self.initial.get('user')
        if not (user and (user.is_superuser or getattr(user, 'role', '') == 'admin')):
            if self.cleaned_data.get('completed_file'):
                raise forms.ValidationError("You are not allowed to upload a file.")
        return self.cleaned_data.get('completed_file')
