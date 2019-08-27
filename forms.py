from django import forms
from .models import User
import re
from django.contrib.auth import authenticate


def password_validator(password: str):

    if not 8 < len(password) < 32:
        raise forms.ValidationError('Длина пароля должна быть от 8 до 32 символов включительно')

    elif not re.findall(r'[A-Z]', password):
        raise forms.ValidationError('Пароль должен содержать заглавные символы')

    elif not re.findall(r'\d', password):
        raise forms.ValidationError('Пароль должен содержать числовые символы')

    elif re.findall(r'\W', password):
        raise forms.ValidationError('Пароль не должен содержать специальные символы')

    return password


def name_validator(name):
    if name and len(name) < 41:

        name_pattern = r'^[A-Za-z0-9][A-Za-z0-9_]+$'

        if re.findall(name_pattern, name):

            if name.endswith('_'):
                raise forms.ValidationError('Имя не должно заканчиваться на _')

            try:  # своеобразная проверка уникальности
                User.objects.get(name=name)
            except User.DoesNotExist:
                return name

            raise forms.ValidationError('Имя пользователя должно быть уникальным')

        raise forms.ValidationError('Имя должно начинаться с [A-Za-z0-9], содержать символы [A-Za-z0-9_]')

    raise forms.ValidationError('Длина имени пользователя должна быть  0 - 40 символ')


def password_field():
    return forms.CharField(max_length=31, widget=forms.PasswordInput)


def find_email(cleaned_data, return_user=False, exception=True):
    email = cleaned_data.get('email')
    email_user = User.objects.get_or_none(email=email)
    if email_user is None:
        return email_user if return_user else email
    if exception:
        raise forms.ValidationError('Пользователь с таким email адресом уже существует')
    return email_user


def check_activated(user):
    if not user.activated:
        raise forms.ValidationError('Аккаунт не активирован, пожалуйста, подтвердите email адрес')
    return user


def check_active(user):
    if not user.is_active:
        raise forms.ValidationError('Аккаунт заблокирован!')
    return user


def check_fine_user(user):
    user = check_active(user)
    return check_activated(user)


class RegisterForm(forms.ModelForm):

    password = password_field()

    class Meta:
        model = User
        fields = ['name', 'email']

    def clean_email(self):
        return find_email(self.cleaned_data)

    def clean_password(self):
        return password_validator(self.cleaned_data['password'])

    def clean_name(self):
        return name_validator(self.cleaned_data['name'])


class LoginForm(forms.Form):
    name = forms.CharField(max_length=40)
    password = password_field()
    log_user = None

    def clean_password(self):
        password = self.cleaned_data['password']
        name = self.cleaned_data.get('name')

        log_user = authenticate(name=name, password=password)
        if log_user is not None:

            log_user = check_activated(log_user)
            log_user = check_active(log_user)

            self.log_user = log_user
            return password

        raise forms.ValidationError('Неверный логин или пароль')


class ResetForm(forms.Form):

    email = forms.EmailField()
    user = None

    def clean_email(self):
        user = find_email(self.cleaned_data, exception=False)
        user = check_fine_user(user)
        if user.activate_key:
            raise forms.ValidationError('Email письмо уже было отправлено! Проверьте почту или спам')

        self.user = user
        return user.email


class NewPasswordForm(forms.Form):
    password = password_field()
    password2 = password_field()
    user = None

    def clean_password(self):
        return password_validator(self.cleaned_data['password'])

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data['password2']

        if password == password2:
            return password2

        raise forms.ValidationError('Пароли не совпали')
