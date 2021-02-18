from django.urls import path

from apps.branch import view
from apps.branch.views import BranchListView, BranchDeleteView
from apps.repository.views import RepositoryDetailView

urlpatterns = [
    path('', BranchListView.as_view(), name='branch_list'),
    path('<int:branch_id>/', RepositoryDetailView.as_view(), name='branch-detail'),
    path('<int:branch_id>/delete/', BranchDeleteView.as_view(), name='branch_delete'),
    path('<int:branch_id>/update/', views.update_branch, name='branch_update'),
]
