from django.urls import path

from ..tag.views import ListTagView, CreateTagView, TagUpdateView

urlpatterns = [
    path('', ListTagView.as_view(), name='repository_tags'),
    path('add/', CreateTagView.as_view(), name='create_tag'),
    path('<int:pk>/edit', TagUpdateView.as_view(), name='edit_tag'),
]
