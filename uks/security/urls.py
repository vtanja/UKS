from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login/', auth_views.LoginView.as_view(template_name='security/login.html'), name='login'),
]
