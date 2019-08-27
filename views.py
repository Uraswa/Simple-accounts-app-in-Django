from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from accounts.models import User
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from datetime import *
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .forms import *



@user_passes_test(lambda user: not user.is_authenticated,login_url = '/')
def loginView(request):
    form = LoginForm()
    if request.method == 'POST':
        
        form = LoginForm(request.POST)
        if form.is_valid():
                       
            login(request, form.log_user)
            next = request.GET.get('next')
            next = next if next else '/'
            return redirect(next)

    return render(request,"login.html",{'form':form})

    

@user_passes_test(lambda user: not user.is_authenticated,login_url = '/')
def registerView(request):
    form = RegisterForm()
    if request.method == 'POST':
        
        form = RegisterForm(request.POST)
        if form.is_valid():
            User.objects.create_user(form.cleaned_data)
            return HttpResponse('Письмо с подтверждением регистрации отправлено')
            
    return render(request,"register.html",{'form':form})

@user_passes_test(lambda user: not user.is_authenticated,login_url = '/')
def activateView(request,key):
    if request.method == 'GET':
        user = User.objects.get_or_none(activate_key = key, activated = False)
        
        if user:
            
            month = user.reg_date.month
            day = user.reg_date.day
            year = user.reg_date.year
            date_1 = datetime.strptime("{}/{}/{}".format(month,day,year), "%m/%d/%Y")

            end_date = date_1 + timedelta(days=2)
            today = datetime.now()
            
            
            if end_date > today:
                user.activated = True 
                user.activate_key = ''
                user.save()
                login(request,user)                
                return render(request,'activate_success.html',{})
            else:
                user.delete()  
        return HttpResponse(('Ошибка'))

@login_required(login_url="accounts/login")
def logoutView(request):
    logout(request)
    return redirect('/accounts/login')

@user_passes_test(lambda user: not user.is_authenticated,login_url = '/')
def resetView(request):

    form = ResetForm()
    if request.method == 'POST':
        form = ResetForm(request.POST)
        
        if form.is_valid():
            activation_key = ''
            while True:
                activation_key = get_random_string(length=60)
                
                if not User.objects.get_or_none(activate_key = activation_key,activated = True):
                    break

            user = form.user
            user.activate_key = activation_key
            user.save()
            msg = render_to_string('reset_pass_email.html',{'key':activation_key,'http':settings.PROTOCOL,'hostname':settings.HOSTNAME})

            send_mail(
                'Смена пароля',
                '',
                settings.EMAIL_HOST_USER,
                [form.cleaned_data['email']],
                html_message=msg
            )

    return render(request,"reset.html",{'form':form})


@user_passes_test(lambda user: not user.is_authenticated,login_url = '/')
def newpasswordView(request,key):
    
    
    user = User.objects.get_or_none(activated = True,activate_key = key)
    if not user:
        return redirect('/')

    form = NewPasswordForm()    
    if request.method == 'POST':
        form = NewPasswordForm(request.POST)
        
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.activate_key = ''
            user.save()
            login(request,user)
            return HttpResponse('Вы успешно сменили пароль')

    return render(request,'newpassword.html',{'form':form})

    