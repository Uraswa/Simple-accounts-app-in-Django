# accounts.forms.py
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User
from django.utils.html import escape
import re
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate


def passwordValidator(password):
    if (password):

        password_len = len(password)
        if (password_len < 8 or password_len > 32):
            raise forms.ValidationError('Длина пароля должна быть от 8 до 32 символов включительно')
            
        any_caps = re.findall(r'[A-Z]',password)
        if (not any_caps):
            raise forms.ValidationError('Пароль должен содержать заглавные символы')

        any_digits = re.findall(r'\d',password)
        if (not any_digits):
            raise forms.ValidationError('Пароль должен содержать числовые символы')

        some_specialchars = re.findall(r'\W',password)
        if (some_specialchars):
            raise forms.ValidationError('Пароль не должен содержать специальные символы')

        return password                    


    raise forms.ValidationError('Введите пароль')

class RegisterForm(forms.Form):
    
    email = forms.EmailField()
    name  = forms.CharField(min_length=1, max_length= 40)
    sername = forms.CharField(min_length=1, max_length=40)
    password = forms.CharField(min_length=8, max_length=31)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("Аккаунт с таким email уже существует")

        if (not len(email)):
            raise forms.ValidationError('Введите ваш email')    

        return escape(email)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if (name and len(name) < 41):
            return escape(name)

        raise forms.ValidationError('Длина имени пользователя должна быть  0 - 40 символ')

    def clean_sername(self):
        sername = self.cleaned_data.get('sername')
        if (sername and len(sername) < 41):
            return escape(sername)

        raise forms.ValidationError('Длина фамилии пользователя должна быть 0 - 40 символ')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return passwordValidator(password)
        

class LoginForm(forms.Form):
    
    email = forms.EmailField()
    password = forms.CharField(max_length=32)

    def clean_email(self):
        email = self.cleaned_data['email']

        

        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        email = self.cleaned_data.get('email')

        user = authenticate(username = email,password = password)

        if (user is not None):

            if not user.is_active:
                raise forms.ValidationError('Ваш аккаунт был заблокирован')

            if not user.activated:
                raise forms.ValidationError('Подтвердите свой email, прежде чем авторизоваться ')  

            return password

        raise forms.ValidationError('Неверный логин или пароль')    
        
   


class ResetForm(forms.Form):
    
    email = forms.CharField()

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            raise forms.ValidationError('Пользователя с таким email адрессом не существует') 

        if (user.activated == False):
            raise forms.ValidationError('Пользователя с таким email адрессом не существует')

        if (user.activate_key):
            raise forms.ValidationError('Email письмо уже было отправлено! Проверьте почту или спам')

        
        return email

class NewPasswordForm(forms.Form):
    
    password = forms.CharField(max_length=32)
    password2 = forms.CharField(max_length=32)

    def clean_password(self):
        password = self.cleaned_data['password']

        return passwordValidator(password)

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data['password2']

        if (password == password2):
            return password2

        raise forms.ValidationError('Пароли не совпали')    


                


    