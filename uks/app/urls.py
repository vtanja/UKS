from django.urls import path, include

urlpatterns = [
    path('', include('app.user.urls')),
    path('user/', include('app.user.urls')),
    path('milestone/', include('app.milestone.urls')),
]
