from django.urls import path
from apps.branch.views import BranchListView

urlpatterns = [
    path('', BranchListView.as_view(), name='branch_list'),
]
