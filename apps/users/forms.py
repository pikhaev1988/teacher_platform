from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=True, label='Имя')
    last_name = forms.CharField(required=True, label='Фамилия')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email


class CustomUserChangeForm(UserChangeForm):
    """Форма редактирования профиля"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'avatar')