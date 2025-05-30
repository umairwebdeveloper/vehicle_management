from django import forms
from django.contrib.auth.models import User
from .validation import *
from .models import Profile

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget = forms.PasswordInput)
    password2 = forms.CharField(label="Repeat Password", widget = forms.PasswordInput)

    class Meta():
        model = User
        fields = ['username', 'email']
        password1 = forms.CharField(label="Password", widget = forms.PasswordInput)
        password2 = forms.CharField(label="Repeat Password", widget = forms.PasswordInput)
        
    def clean(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        error_list = dict()
        
        verify_password(field_name='password1', password1=password1, password2=password2, error_list=error_list)
        
        if User.objects.filter(email=email).exists():
            error_list['email'] = 'Email already registered!'
        
        if User.objects.filter(username=username).exists():
            error_list['username'] = 'Username already registered!'

        if error_list is not None:
            for error in error_list:
                error_message = error_list[error]
                self.add_error(error, error_message)
                
        return self.cleaned_data


class LoginForm(forms.Form):
    email = forms.CharField(label="Email or Username")
    password = forms.CharField(label="Password", widget = forms.PasswordInput)


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label="Old Password", widget=forms.PasswordInput)
    password1 = forms.CharField(label="Set Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image", "bio"]  
        widgets = {
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            max_size = 5 * 1024 * 1024
            if image.size > max_size:
                raise forms.ValidationError("Image file too large ( > 5 MB ).")
        return image
