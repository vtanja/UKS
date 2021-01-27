from django.urls import path

from app.user import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('profile', views.profile, name='profile'),
    path('repository/', views.addRepository, name='repository'),
    path('detail/?P<int:id>/', views.detail, name='detail'),
]
