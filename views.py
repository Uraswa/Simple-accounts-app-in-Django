from django.shortcuts import render
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from datetime import *
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .forms import *


@user_passes_test(lambda user: not user.is_authenticated, login_url='/')
def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        
        form = LoginForm(request.POST)
        if form.is_valid():
                       
            login(request, form.log_user)
            next_path = request.GET.get('next')
            next_path = next_path if next_path else '/'
            return redirect(next_path)

    return render(request, "login.html", {'form': form})

    
@user_passes_test(lambda user: not user.is_authenticated, login_url='/')
def register_view(request):
    form = RegisterForm()
    if request.method == 'POST':
        
        form = RegisterForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            User.objects.create_user(name=name, email=email, password=password)
            return HttpResponse('Письмо с подтверждением регистрации отправлено')

    return render(request, 'register.html', {'form': form})


@user_passes_test(lambda user: not user.is_authenticated, login_url='/')
def activate_view(request, key):
    if request.method == 'GET':
        user = User.objects.get_or_none(activate_key=key, activated=False)
        
        if user:
            
            month = user.reg_date.month
            day = user.reg_date.day
            year = user.reg_date.year
            date_1 = datetime.strptime("{}/{}/{}".format(month, day, year), "%m/%d/%Y")

            end_date = date_1 + timedelta(days=2)
            today = datetime.now()
            
            if end_date > today:
                user.activated = True 
                user.activate_key = ''
                user.save()
                login(request, user)
                return render(request, 'activate_success.html', {})
            else:
                user.delete()  
        return HttpResponse('Ошибка')


@login_required(login_url="accounts/login")
def logout_view(request):
    logout(request)
    return redirect('/accounts/login')


@user_passes_test(lambda user: not user.is_authenticated, login_url='/')
def reset_view(request):

    form = ResetForm()
    if request.method == 'POST':
        form = ResetForm(request.POST)
        
        if form.is_valid():
            while True:
                activation_key = get_random_string(length=60)
                
                if not User.objects.get_or_none(activate_key=activation_key, activated=True):
                    break

            user = form.user
            user.activate_key = activation_key
            user.save()
            msg = render_to_string('email_templates/reset_pass_email.html',
                                   {'key': activation_key, 'http': settings.PROTOCOL, 'hostname': settings.HOSTNAME})

            send_mail(
                'Смена пароля',
                '',
                settings.EMAIL_HOST_USER,
                [form.cleaned_data['email']],
                html_message=msg
            )

    return render(request, "reset.html", {'form': form})


@user_passes_test(lambda user: not user.is_authenticated, login_url='/')
def new_password_view(request, key):
    
    user = User.objects.get_or_none(activated=True, activate_key=key)
    if not user:
        return redirect('/')

    form = NewPasswordForm()    
    if request.method == 'POST':
        form = NewPasswordForm(request.POST)
        
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.activate_key = ''
            user.save()
            login(request, user)
            return HttpResponse('Вы успешно сменили пароль')

    return render(request, 'new_password.html', {'form': form})
