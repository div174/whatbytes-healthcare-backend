"""URL Configuration for healthcare_backend project."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # All Healthcare API routes start with api/
    path('api/', include('api.urls')),
]
