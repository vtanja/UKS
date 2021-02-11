from django.urls import path, include

from .views import ListLabelView, CreateLabel, LabelEdit, LabelDeleteView

urlpatterns = [
    path('', ListLabelView.as_view(), name='repository_labels'),
    path('add/', CreateLabel.as_view(), name='create_label'),
    path('edit/<int:pk>', LabelEdit.as_view(), name='label-edit'),
    path('delete/<int:pk>', LabelDeleteView.as_view(), name='label-delete'),
]