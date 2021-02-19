from django.urls import path, include

from ..repository.views import RepositoryDetailView, add_repository, add_collaborators, \
    CollaboratorsDeleteView, manage_access, options, RepositoryUpdateView, RepositoryDeleteView, repository_settings

urlpatterns = [
    path('<int:pk>/', RepositoryDetailView.as_view(), name='detail'),
    path('add/', add_repository, name='add'),
    path('<int:repo_id>/branch/', include('apps.branch.urls')),
    path('<int:repository_id>/issues/', include('apps.issue.urls')),
    path('<int:repo_id>/milestones/', include('apps.milestone.urls')),
    path('<int:id>/labels/', include('apps.label.urls')),
    path('<int:key>/settings/', repository_settings, name='repository_settings'),
    path('addCollaborators/', add_collaborators, name='addCollaborators'),
    path('delete/<int:pk>', CollaboratorsDeleteView.as_view(), name='collaborators-delete'),
    path('<int:repo_id>/projects/', include('apps.project.urls')),
    path('<int:key>/manageAccess', manage_access, name='manage_access'),
    path('<int:key>/options', options, name='options'),
    path('<int:pk>/edit', RepositoryUpdateView.as_view(), name='repository_update'),
    path('<int:pk>/delete', RepositoryDeleteView.as_view(), name='repository_delete'),
    path('<int:id>/tag/', include('apps.tag.urls')),
    path('<int:repo_id>/wiki/', include('apps.wiki.urls')),
]
