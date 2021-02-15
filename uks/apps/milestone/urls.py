from django.urls import path

from .views import MilestoneListView, CreateMilestoneView, MilestoneDetailView, MilestoneUpdateView, close_milestone, \
    MilestoneDeleteView

urlpatterns = [
    path('', MilestoneListView.as_view(), name='repository_milestones'),
    path('add/', CreateMilestoneView.as_view(), name='create_milestone'),
    path('<int:pk>/', MilestoneDetailView.as_view(), name='milestone_details'),
    path('<int:pk>/update', MilestoneUpdateView.as_view(), name='milestone_update'),
    path('<int:pk>/close/', close_milestone, name='milestone_close'),
    path('<int:pk>/delete', MilestoneDeleteView.as_view(), name='milestone_delete'),
]
