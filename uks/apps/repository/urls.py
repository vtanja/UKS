from django.urls import path, include

from apps.repository import views
from apps.repository.views import RepositoryDetailView

urlpatterns = [
    path('<int:pk>/', RepositoryDetailView.as_view(), name='detail'),
    path('add/', views.add_repository, name='add'),
    path('<int:id>/branch/', include('apps.branch.urls')),
    path('<int:repository_id>/issues/', include('apps.issue.urls')),
    path('<int:id>/milestones/', include('apps.milestone.urls')),
    path('<int:id>/labels/', include('apps.label.urls')),
    path('<int:id>/projects/', include('apps.project.urls')),
    path('<int:id>/wiki/', include('apps.wiki.urls')),
]
