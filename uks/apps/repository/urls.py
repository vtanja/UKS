from django.urls import path, include

from apps.repository import views

urlpatterns = [
    path('<int:id>/', views.detail, name='detail'),
    path('<int:id>/milestones/', include('apps.milestone.urls'))
]
