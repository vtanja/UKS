from django.urls import path

from apps.branch import views
from apps.branch.views import BranchListView, BranchDeleteView
from apps.repository.views import RepositoryDetailView

urlpatterns = [
    path('', BranchListView.as_view(), name='branch_list'),
    path('<int:pk>/', RepositoryDetailView.as_view(), name='branch-detail'),
    path('<int:pk>/delete/', BranchDeleteView.as_view(), name='branch_delete'),
    path('<int:pk>/update/', views.update_branch, name='branch_update'),
]
