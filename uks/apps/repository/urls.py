from django.urls import path, include

from ..repository import views
from ..repository.views import RepositoryDetailView, RepositorySettings, CollaboratorsDeleteView

urlpatterns = [
    path('<int:pk>/', RepositoryDetailView.as_view(), name='detail'),
    path('add/', views.add_repository, name='add'),
    path('<int:id>/branch/', include('apps.branch.urls')),
    path('<int:repository_id>/issues/', include('apps.issue.urls')),
    path('<int:repo_id>/milestones/', include('apps.milestone.urls')),
    path('<int:id>/labels/', include('apps.label.urls')),
    path('<int:id>/settings/', RepositorySettings, name='repository_settings'),
    path('addCollaborators/', views.addCollaborators, name='addCollaborators'),
    path('delete/<int:pk>', CollaboratorsDeleteView.as_view(), name='collaborators-delete'),
    path('<int:repo_id>/projects/', include('apps.project.urls')),
    path('<int:id>/wiki/', include('apps.wiki.urls')),

]
