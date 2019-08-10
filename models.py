from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.utils.html import escape
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from PROJECT_DIR.settings import HOSTNAME,PROTOCOL,EMAIL_HOST_USER as admin_email

# Это простое приложение авторизации, которое я использую в своих проектах
# Для работы нужно определить Имя хоста, протокол http:// или https:// 
# И указать залогинется в вашей почте в settings
# И изменить PROJECT_DIR.settings на модуль ваших настроек



class UserManager(BaseUserManager):
    def create_user(self, email,name,sername,password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        activation_key = ''
        while (True):
            activation_key = get_random_string(length=60)
            try: 
                if (not User.objects.get(activate_key = activation_key)):
                    break
            except User.DoesNotExist:
                break        

        user = self.model(
            email=self.normalize_email(email),
            name = escape(name),
            sername = escape(sername),
            activate_key = activation_key
        )

        user.set_password(password)
        user.save(using=self._db)

        msg = render_to_string('activate.html',{'key':activation_key,'http':PROTOCOL,'hostname':HOSTNAME})

        send_mail(
            'Подтверждение регистрации',
            '',
            admin_email
            [email],
            html_message=msg
        )

        return user

    def create_staffuser(self, email, password,name = '',sername = ''):
        """
        Creates and saves a staff user with the given email and password.
        """
        

        user = self.create_user(
            email,
            name=name,
            sername=sername,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password,name = '',sername = ''):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            name=name,
            sername=sername,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user 

    
          

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    
    name = models.CharField(max_length = 255)
    sername = models.CharField(max_length = 255)
    activated = models.BooleanField(default=False)
    activate_key = models.CharField(max_length = 255,null = True,blank= True)
    reg_date = models.DateTimeField(auto_now_add=True,null = True, blank = True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False) # a superuser
    # notice the absence of a "Password field", that's built in.

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Email & Password are required by default.
    objects = UserManager()

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        
        return self.staff

    @property
    def is_admin(self):
        
        return self.admin

    @property
    def is_active(self):
        
        return self.active
