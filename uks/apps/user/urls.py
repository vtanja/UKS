from django.urls import path
from django.contrib.auth import views as auth_views

from apps.user import views
from .views import AllIssuesListView, MyPasswordResetView, MyPasswordResetDoneView, MyPasswordResetConfirmView, \
    MyPasswordResetCompleteView, SearchResultsView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('<int:pk>/profile/', views.profile, name='profile'),
    path('password-reset/', MyPasswordResetView.as_view(), name='password-reset'),
    path('password-reset/done/', MyPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', MyPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('issues/', AllIssuesListView.as_view(), name='all-user-issues'),
    path('search', SearchResultsView.as_view(), name='search_results')
]
