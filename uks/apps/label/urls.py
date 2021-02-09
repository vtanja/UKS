from django.urls import path, include

from .views import ListLabelView

urlpatterns = [
    path('', ListLabelView.as_view(), name='repository_labels'),
]