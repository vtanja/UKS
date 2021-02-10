from django.urls import path

from .views import ProjectListView, CreateProjectView

urlpatterns = [
    path('', ProjectListView.as_view(), name='repository_projects'),
    path('add/', CreateProjectView.as_view(), name='create_project'),
]
