from django.urls import path

from ..tag.views import ListTagView

urlpatterns = [
    path('', ListTagView.as_view(), name='repository_tags'),
]
