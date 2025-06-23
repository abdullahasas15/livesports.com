
# livesports_project/apps/viewer/urls.py
from django.urls import path
from . import views

app_name = 'viewer' # IMPORTANT: Define app_name for namespacing

urlpatterns = [
    path('tournaments/', views.viewer_tournament_list_view, name='tournament_list'),
    path('tournament-details/<int:tournament_id>/', views.viewer_tournament_details_view, name='tournament_details'),
    path('signup/', views.viewer_signup_view, name='signup'), # NEW URL for Viewer Signup
    path('profile/', views.viewer_profile_view, name='profile'), # NEW URL for Viewer Profile
]