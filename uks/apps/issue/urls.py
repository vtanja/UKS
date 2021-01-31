from django.urls import path
from .views import IssuesListView, IssueDetailView

urlpatterns = [
    path('', IssuesListView.as_view(), name='repository_issues'),
    path('<int:pk>/', IssueDetailView.as_view(), name='issue-details'),
]
