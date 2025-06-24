# livesports_project/apps/scores/urls.py
from django.urls import path
from . import views

app_name = 'scores'

urlpatterns = [
    # Example: path('cricket/live/<int:match_id>/', views.cricket_live_score_view, name='cricket_live'),
    # Example: path('cricket/admin/<int:match_id>/', views.cricket_admin_score_view, name='cricket_admin'),

    # Generic URLs for Admin Match Detail Page (e.g., /scores/chess/admin/123/)
    path('<str:game_name>/admin/<int:match_id>/', views.admin_match_detail_view, name='admin_match_detail'),
    # Generic URLs for Viewer Live Match Page (e.g., /scores/chess/live/123/)
    path('<str:game_name>/live/<int:match_id>/', views.viewer_live_match_view, name='viewer_match_detail'),
]