# livesports_project/apps/scores/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.tournaments.models import Match, Game, Team # Import models
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

def kabaddi_admin_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    team1 = match.team1
    team2 = match.team2
    # Get real player names from match fields
    team1_players = [getattr(match, f'kabaddi_player{i}_team1', f'{team1.name} Player {i}') for i in range(1, 8)]
    team2_players = [getattr(match, f'kabaddi_player{i}_team2', f'{team2.name} Player {i}') for i in range(1, 8)]
    players = [p for p in team1_players if p] + [p for p in team2_players if p]
    context = {
        'match': match,
        'team1': team1,
        'team2': team2,
        'players': players,
        'match_id': match.id,
    }
    return render(request, 'scores/kabaddi_admin.html', context)

def kabaddi_live_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    team1 = match.team1
    team2 = match.team2
    team1_players = [getattr(match, f'kabaddi_player{i}_team1', f'{team1.name} Player {i}') for i in range(1, 8)]
    team2_players = [getattr(match, f'kabaddi_player{i}_team2', f'{team2.name} Player {i}') for i in range(1, 8)]
    players = [p for p in team1_players if p] + [p for p in team2_players if p]
    context = {
        'match': match,
        'team1': team1,
        'team2': team2,
        'players': players,
        'match_id': match.id,
    }
    return render(request, 'scores/kabaddi_live.html', context)

