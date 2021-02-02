from django.urls import path

from apps.issue import views

urlpatterns = [
    # path('', views.issues, name='all-issues'),
    path('all', views.issues, name='all-issues'),
]