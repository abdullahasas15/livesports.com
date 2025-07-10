# livesports_project/apps/scores/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.tournaments.models import Match, Game # Import models
from django.utils.text import slugify  # <-- Add this import

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

    # Use slugified game_name for template lookup
    template_slug = slugify(game_name)
    return render(request, f'scores/{template_slug}_admin.html', {
        'match': match, # Pass the full match object
        'game': game,
        'tournament': match.tournament, # Pass tournament context
    })

def viewer_live_match_view(request, game_name, match_id):
    """
    Viewer's live page for a specific match. Displays scores in real-time.
    """
    game = get_object_or_404(Game, name__iexact=game_name)
    match = get_object_or_404(Match, id=match_id, game=game)

    # Use slugified game_name for template lookup
    template_slug = slugify(game_name)
    return render(request, f'scores/{template_slug}_live.html', {
        'match': match, # Pass the full match object
        'game': game,
        'tournament': match.tournament, # Pass tournament context
    })

