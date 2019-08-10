from django.urls import path,include
from .views import loginView,registerView,activateView,logoutView,resetView,newpasswordView

urlpatterns = [
    path('new_password/<str:key>',newpasswordView,name='new_pass'),
    path('reset_pass',resetView,name="reset_pass"),
    path('logout',logoutView,name="logoutView"),
    path('login',loginView,name="loginView"),
    path('registration',registerView,name="Register"),
    path('activate/<str:key>',activateView,name="Activate")
]