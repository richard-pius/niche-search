from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class SearchForm(forms.Form):
    q = forms.CharField(label='Search', max_length=100, required=False)

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    class Meta:
        model = UserProfile
        fields = ['profile_picture']
    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user_instance:
            self.fields['username'].initial = self.user_instance.username
            self.fields['email'].initial = self.user_instance.email
    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user_instance:
            self.user_instance.username = self.cleaned_data['username']
            self.user_instance.email = self.cleaned_data['email']
            if commit:
                self.user_instance.save()
        if commit:
            profile.save()
        return profile