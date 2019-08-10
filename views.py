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
from Vtalk.settings import HOSTNAME,PROTOCOL
from .forms import *



@user_passes_test(lambda user: not user.is_authenticated,login_url = '/')
def loginView(request):
    if request.method == 'POST':
        
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            
            login(request, user)
            next = request.GET.get('next')
            next = next if next else '/'
            return redirect(next)

        return render(request,'login.html',{'form':form})            

    form = LoginForm()
    return render(request,"login.html",{'form':form})

    

@user_passes_test(lambda user: not user.is_authenticated,login_url = '/')
def registerView(request):
    form = RegisterForm()
    if request.method == 'POST':
        
        form = RegisterForm(request.POST)
        if form.is_valid():
            User.objects.create_user(form.cleaned_data['email'],form.cleaned_data['name'],form.cleaned_data['sername'],form.cleaned_data['password'])
            return HttpResponse('Письмо с подтверждением регистрации отправлено')
            
    return render(request,"register.html",{'form':form})

@user_passes_test(lambda user: not user.is_authenticated,login_url = '/')
def activateView(request,key):
    if request.method == 'GET':
        try:
            user = User.objects.get(activate_key = key, activated = False)
        except User.DoesNotExist:
            user = None
        if (user):
            
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

    if request.method == 'POST':
        form = ResetForm(request.POST)
        valid = form.is_valid()
        if (valid):
            activation_key = ''
            while (True):
                activation_key = get_random_string(length=60)
                try: 
                    if (not User.objects.get(activate_key = activation_key,activated = True)):
                        break
                except User.DoesNotExist:
                    break

            user = User.objects.get(email = form.cleaned_data['email'])
            user.activate_key = activation_key
            user.save()
            msg = render_to_string('reset_pass_email.html',{'key':activation_key,'http':PROTOCOL,'hostname':HOSTNAME})

            send_mail(
                'Смена пароля Vtalk',
                '',
                'rockavova@gmail.com',
                [form.cleaned_data['email']],
                html_message=msg
            )

        return render(request,"reset.html",{'form':form})

    form = ResetForm()

    return render(request,"reset.html",{'form':form})




@user_passes_test(lambda user: not user.is_authenticated,login_url = '/')
def newpasswordView(request,key):
    
    try:
        user = User.objects.get(activated = True,activate_key = key)
    except User.DoesNotExist:
        return redirect('/')

    if request.method == 'POST':
        form = NewPasswordForm(request.POST)
        
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.activate_key = ''
            user.save()
            login(request,user)
            return HttpResponse('Вы успешно сменили пароль')

        return render(request,'newpassword.html',{'form':form})    

    form = NewPasswordForm()
    return render(request,'newpassword.html',{'form':form})    