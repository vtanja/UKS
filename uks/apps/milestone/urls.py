from django.urls import path

from .views import MilestoneListView

urlpatterns = [
    path('', MilestoneListView.as_view(), name='repository_milestones'),
]
