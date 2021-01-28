from django.urls import path

from app.repository import views

urlpatterns = [
    path('detail/?P<int:id>/', views.detail, name='detail'),
]
