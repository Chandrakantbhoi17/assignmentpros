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
    due_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )
    )
    
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
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter task title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter task description'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'completed_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        from accounts.models import User
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Save user for clean validation
        self.initial['user'] = user

        # Configure fields based on user role
        if user and (user.is_superuser or getattr(user, 'role', '') == 'admin'):
            # Admin can assign to any user
            self.fields['assigned_to'].queryset = User.objects.all()
            self.fields['assigned_to'].empty_label = "Select a user"
        else:
            # Students can only edit description
            self.fields['title'].disabled = True
            self.fields['title'].required = False
            self.fields['due_date'].disabled = True
            self.fields['due_date'].required = False
            self.fields['assigned_to'].disabled = True
            self.fields['assigned_to'].required = False
            self.fields['status'].disabled = True
            self.fields['status'].required = False
            self.fields['amount'].disabled = True
            self.fields['amount'].required = False
            self.fields['completed_file'].widget = forms.HiddenInput()
            self.fields['completed_file'].required = False

    def clean(self):
        cleaned_data = super().clean()
        user = self.initial.get('user')
        
        # For students, preserve original values for disabled fields
        if not (user and (user.is_superuser or getattr(user, 'role', '') == 'admin')):
            if self.instance.pk:  # Only for existing tasks
                cleaned_data['title'] = self.instance.title
                cleaned_data['due_date'] = self.instance.due_date
                cleaned_data['assigned_to'] = self.instance.assigned_to
                cleaned_data['status'] = self.instance.status
                cleaned_data['amount'] = self.instance.amount
                cleaned_data['completed_file'] = self.instance.completed_file
        
        return cleaned_data

    def clean_completed_file(self):
        user = self.initial.get('user')
        if not (user and (user.is_superuser or getattr(user, 'role', '') == 'admin')):
            if self.cleaned_data.get('completed_file'):
                raise forms.ValidationError("You are not allowed to upload a file.")
        return self.cleaned_data.get('completed_file')
