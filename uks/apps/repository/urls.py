from django.urls import path, include

from ..repository import views
from ..repository.views import RepositoryDetailView, repository_settings, CollaboratorsDeleteView

urlpatterns = [
    path('<int:pk>/', RepositoryDetailView.as_view(), name='detail'),
    path('add/', views.add_repository, name='add'),
    path('<int:id>/branch/', include('apps.branch.urls')),
    path('<int:repository_id>/issues/', include('apps.issue.urls')),
    path('<int:repo_id>/milestones/', include('apps.milestone.urls')),
    path('<int:id>/labels/', include('apps.label.urls')),
    path('<int:key>/settings/', repository_settings, name='repository_settings'),
    path('addCollaborators/', views.add_collaborators, name='addCollaborators'),
    path('delete/<int:pk>', CollaboratorsDeleteView.as_view(), name='collaborators-delete'),
    path('<int:repo_id>/projects/', include('apps.project.urls')),
    path('<int:repo_id>/wiki/', include('apps.wiki.urls')),

]
