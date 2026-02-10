from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].help_text = None # Remove verbose help text
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {field.replace("_", " ")}'
            })
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email (Optional)'})

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter {field}'
            })
