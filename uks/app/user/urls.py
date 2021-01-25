from django.urls import path

from app.user import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile', views.profile, name='profile'),
]
