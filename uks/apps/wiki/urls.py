from django.urls import path

from apps.wiki import views
from apps.wiki.views import WikiListView

urlpatterns = [
    path('', WikiListView.as_view(), name='wiki-overview'),
]