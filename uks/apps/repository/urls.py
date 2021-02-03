from django.urls import path

from apps.repository import views

urlpatterns = [
    path('<int:id>/', views.detail, name='detail'),
]
