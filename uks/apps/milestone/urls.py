from django.urls import path

from .views import MilestoneListView, CreateMilestoneView

urlpatterns = [
    path('', MilestoneListView.as_view(), name='repository_milestones'),
    path('add/', CreateMilestoneView.as_view(), name='create_milestone'),
]
