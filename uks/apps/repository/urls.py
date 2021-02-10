from django.urls import path, include

from apps.repository import views

urlpatterns = [
    path('<int:id>/', views.detail, name='detail'),
    path('<int:id>/issues/', include('apps.issue.urls')),
    path('<int:id>/milestones/', include('apps.milestone.urls')),
    path('<int:id>/labels/', include('apps.label.urls')),
    path('<int:id>/projects/', include('apps.project.urls')),
]
