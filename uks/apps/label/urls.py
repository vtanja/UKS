from django.urls import path, include

from .views import ListLabelView, CreateLabel

urlpatterns = [
    path('', ListLabelView.as_view(), name='repository_labels'),
    path('add/', CreateLabel.as_view(), name='create_label'),
]