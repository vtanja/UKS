from django.urls import path
from django.contrib.auth import views as auth_views

from app.user import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('profile', views.profile, name='profile'),
    path('profile/repos', views.repos, name='repos'),
    path('profile/issues', views.issues, name='issues'),
    path('password-reset', auth_views.PasswordResetView.as_view(template_name='user/password_reset.html'),
                        name='password-reset'),
    path('password-reset/done', auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'),
                        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'),
                        name='password_reset_confirm'),
path('password-reset-complete', auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'),
                        name='password_reset_complete'),
]
