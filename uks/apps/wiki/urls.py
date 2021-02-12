from django.urls import path

from apps.wiki.views import WikiListView, WikiDetailPage, CreateWikiView, WikiUpdateView, WikiDeleteView, \
    HistoryListView

urlpatterns = [
    path('', WikiListView.as_view(), name='wiki-overview'),
    path('<int:pk>/', WikiDetailPage.as_view(), name='wiki-details'),
    path('<int:pk>/edit/', WikiUpdateView.as_view(), name='wiki-update'),
    path('<int:pk>/delete/', WikiDeleteView.as_view(), name='wiki-delete'),
    path('<int:pk>/history/', HistoryListView.as_view(), name='wiki-history'),
    path('add/', CreateWikiView.as_view(), name='wiki-add'),
]