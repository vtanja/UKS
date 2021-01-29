from django.urls import path

from apps.repository import views

urlpatterns = [
    path('detail/?P<int:id>/', views.detail, name='detail'),
]
