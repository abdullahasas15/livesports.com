# livesports_project/apps/scores/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.tournaments.models import Match, Game # Import models

@login_required
def admin_match_detail_view(request, game_name, match_id):
    """
    Admin view for a specific match. Allows score updates.
    """
    # Ensure only staff (admins) can access this
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home:home') # Redirect non-staff users

    game = get_object_or_404(Game, name__iexact=game_name) # Case-insensitive game name lookup
    match = get_object_or_404(Match, id=match_id, game=game) # Ensure match belongs to this game

    # Here you would add logic for score updates (POST request)
    # For now, just render the template
    
    return render(request, f'scores/{game_name.lower()}_admin.html', {
        'match': match,
        'game': game,
        'tournament': match.tournament, # Pass tournament context
    })

def viewer_live_match_view(request, game_name, match_id):
    """
    Viewer's live page for a specific match. Displays scores in real-time.
    """
    game = get_object_or_404(Game, name__iexact=game_name)
    match = get_object_or_404(Match, id=match_id, game=game)

    # Here you would integrate WebSocket logic for live updates
    # For now, just render the template
    
    return render(request, f'scores/{game_name.lower()}_live.html', {
        'match': match,
        'game': game,
        'tournament': match.tournament, # Pass tournament context
    })
