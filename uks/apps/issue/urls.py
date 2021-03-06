from django.urls import path
from .views import IssuesListView, IssueDetailView, CreateIssueView, IssueUpdateView, close_issue

urlpatterns = [
    path('', IssuesListView.as_view(), name='repository-issues'),
    path('<int:pk>/', IssueDetailView.as_view(), name='issue-details'),
    path('<int:pk>/edit/', IssueUpdateView.as_view(), name='issue-update'),
    path('add/', CreateIssueView.as_view(), name='issue-add'),
    path('<int:pk>/close/', close_issue, name='issue-close'),
]
