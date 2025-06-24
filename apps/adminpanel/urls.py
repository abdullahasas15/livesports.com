# livesports_project/apps/adminpanel/urls.py
from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('auth/', views.user_auth_view, name='user_auth'), # Renamed from login_signup
    path('logout/', views.admin_logout_view, name='logout'),
    path('create-tournament/', views.create_tournament_view, name='create_tournament'),
    path('dashboard/', views.admin_dashboard_view, name='dashboard'),
    path('manage-matches/<int:tournament_id>/', views.manage_matches_view, name='manage_matches'),
    path('matches-configured/', views.matches_configured_view, name='matches_configured'),
    path('tournament-details/<int:tournament_id>/', views.tournament_details_view, name='tournament_details'),
    path('add-matches/<int:tournament_id>/<int:game_id>/', views.add_more_matches_view, name='add_more_matches'),
]
