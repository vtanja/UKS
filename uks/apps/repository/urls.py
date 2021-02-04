from django.urls import path, include

from apps.repository import views
from apps.repository.views import RepositoryDetailView

urlpatterns = [
    path('<int:pk>/', RepositoryDetailView.as_view(), name='detail'),
    # path('<int:pk>/overview', RepositoryDetailView.as_view(), name='overview'),
    path('add', views.addRepository, name='add'),
    path('<int:pk>/branch/', include('apps.branch.urls')),
]
