from django.urls import path, include

from ..insights.views import IssueStatisticsView, CommitStatisticsView, MilestoneStatisticsView
from ..repository.views import RepositoryDetailView, add_repository, add_collaborators, \
    CollaboratorsDeleteView, manage_access, options, RepositoryUpdateView, RepositoryDeleteView, repository_settings, \
    RepositoryUpdateVisibilityView, RepositoryInsightsView

urlpatterns = [
    path('<int:pk>/', RepositoryDetailView.as_view(), name='detail'),
    path('add/', add_repository, name='add'),
    path('<int:pk>/branch/', include('apps.branch.urls')),
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
    path('<int:pk>/editVisibility', RepositoryUpdateVisibilityView.as_view(), name='repository_visibility_update'),
    path('<int:repository_id>/insights/', RepositoryInsightsView.as_view(), name='repository-insights'),
    path('<int:repository_id>/insights/issues/', IssueStatisticsView.as_view(), name='issue-statistics'),
    path('<int:repository_id>/insights/commits/', CommitStatisticsView.as_view(), name='commit-statistics'),
    path('<int:repository_id>/insights/milestone/', MilestoneStatisticsView.as_view(), name='milestone-statistics'),
]
