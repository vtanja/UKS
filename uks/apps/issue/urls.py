from django.urls import path
from .views import IssuesListView, IssueDetailView, CreateIssueView

urlpatterns = [
    path('', IssuesListView.as_view(), name='repository_issues'),
    path('<int:pk>/', IssueDetailView.as_view(), name='issue_details'),
    path('add/', CreateIssueView.as_view(), name='issue_add'),
]
