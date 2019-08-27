from django.urls import path
from .views import login_view, register_view, activate_view, logout_view, reset_view, new_password_view

urlpatterns = [
    path('new_password/<str:key>', new_password_view, name='new_pass'),
    path('reset_pass', reset_view, name="reset_pass"),
    path('logout', logout_view, name="logoutView"),
    path('login', login_view, name="loginView"),
    path('registration', register_view, name="Register"),
    path('activate/<str:key>', activate_view, name="Activate")
]
