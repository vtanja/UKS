from django.urls import path
from apps.branch.views import BranchListView, BranchDeleteView

urlpatterns = [
    path('', BranchListView.as_view(), name='branch_list'),
    path('<int:pk>/delete/', BranchDeleteView.as_view(), name='branch_delete'),
]
