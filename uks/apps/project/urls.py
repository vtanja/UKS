from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from .views import ProjectListView, CreateProjectView, ProjectDetailView

urlpatterns = [
    path('', ProjectListView.as_view(), name='repository_projects'),
    path('add/', CreateProjectView.as_view(), name='create_project'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project_details'),
    path('ajax/update_issue/', views.update_issue, name='update_issue'),
]
urlpatterns += staticfiles_urlpatterns()
