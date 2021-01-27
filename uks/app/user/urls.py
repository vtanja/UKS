from django.urls import path
from django.contrib.auth import views as auth_views

from app.user import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('profile', views.profile, name='profile'),
    path('password-reset', auth_views.PasswordResetView.as_view(template_name='user/password_reset.html'),
                        name='password-reset'),
]
