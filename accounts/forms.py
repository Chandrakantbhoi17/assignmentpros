from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class StudentSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control",
                "placeholder": f"Enter {field.label}"
            })