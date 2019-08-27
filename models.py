from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.utils.html import escape
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


#BASE MANAGER 


class BaseManager(models.Manager):

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class UserManager(BaseUserManager, BaseManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        if not name:
            raise ValueError('Users must have a name')

        activation_key = ''
        while True:
            activation_key = get_random_string(length=60)
            try:
                if not User.objects.get(activate_key=activation_key):
                    break
            except User.DoesNotExist:
                break

        user = self.model(
            email=self.normalize_email(email),
            name=escape(name),
            activate_key=activation_key
        )

        user.set_password(password)
        user.save(using=self._db)

        msg = render_to_string('email_templates/activate.html', {'key': activation_key, 'http': settings.PROTOCOL, 'hostname': settings.HOSTNAME})

        send_mail(
            'Подтверждение регистрации',
            '',
            settings.EMAIL_HOST_USER,
            [email],
            html_message=msg
        )

        return user

    def create_staffuser(self, email, password, name=''):
        user = self.create_user(
            email,
            name=name,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, name=''):
        user = self.create_user(
            email=email,
            name=name,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.activated = True
        user.activate_key = ''
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    name = models.CharField(unique=True,max_length=40,verbose_name='user name')
    activated = models.BooleanField(default=False)
    activate_key = models.CharField(max_length=255, null=True, blank=True)
    reg_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    avatar = models.ImageField(null=True, blank=True, upload_to='user_avatars')

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def get_avatar(self):
        return f'{settings.PROTOCOL}{settings.HOSTNAME}{self.avatar.url if self.avatar else None}'

    def __str__(self):
        return f'{self.id} {self.email} {self.name}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
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



