from django.urls import path

from apps.wiki.views import WikiListView, WikiDetailPage, CreateWikiView

urlpatterns = [
    path('', WikiListView.as_view(), name='wiki-overview'),
    path('<int:pk>/', WikiDetailPage.as_view(), name='wiki-details'),
    path('add/', CreateWikiView.as_view(), name='wiki-add'),
]