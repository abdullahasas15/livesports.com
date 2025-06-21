# livesports_project/apps/viewer/urls.py
from django.urls import path
from . import views

app_name = 'viewer' # IMPORTANT: Define app_name for namespacing

urlpatterns = [
    path('tournaments/', views.viewer_tournament_list_view, name='tournament_list'),
    # Reusing the tournament_details_view from adminpanel for consistency
    # This URL will also point to the same tournament details view
    path('tournament-details/<int:tournament_id>/', views.viewer_tournament_details_view, name='tournament_details'),
]
