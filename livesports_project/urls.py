"""
URL configuration for livesports_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include # Combine imports
from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.home.urls', namespace='home')), # Added namespace
    path('viewer/', include('apps.viewer.urls', namespace='viewer')), # Added namespace
    path('adminpanel/', include('apps.adminpanel.urls', namespace='adminpanel')), # Added namespace
    path('owner/', include('apps.owner.urls', namespace='owner')), # Added namespace
    path('tournaments/', include('apps.tournaments.urls', namespace='tournaments')), # Added namespace
    path('scores/', include('apps.scores.urls', namespace='scores')), # Added namespace
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # If STATIC_ROOT is not set, or for local testing only:
    # This line is usually redundant if STATIC_ROOT points to your collected static files.
    # If you put static files directly in livesports_project/static, this helps.
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))

# This is often needed for media files if you plan to upload user content
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

