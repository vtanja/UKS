from django.urls import path

from apps.wiki.views import WikiListView, WikiDetailPage

urlpatterns = [
    path('', WikiListView.as_view(), name='wiki-overview'),
    path('<int:pk>/', WikiDetailPage.as_view(), name='wiki-details'),
]