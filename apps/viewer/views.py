# livesports_project/apps/viewer/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q # For search functionality
import json # For JSON serialization
from apps.tournaments.models import Tournament, Team, Game, Match # Import necessary models

def viewer_tournament_list_view(request):
    """
    Displays a list of all tournaments with search functionality for viewers.
    """
    query = request.GET.get('q') # Get the search query from URL parameter 'q'
    
    if query:
        # Search for tournaments by name, or by associated game names (case-insensitive)
        tournaments = Tournament.objects.filter(
            Q(name__icontains=query) | # Search by tournament name
            Q(games__name__icontains=query) # Search by associated game names
        ).distinct().order_by('-start_date') # Use .distinct() to avoid duplicate tournaments if multiple games match
    else:
        # If no query, show all tournaments
        tournaments = Tournament.objects.all().order_by('-start_date')
    
    return render(request, 'viewer_tournament_list.html', {
        'tournaments': tournaments,
        'query': query, # Pass the query back to pre-fill search bar
    })


def viewer_tournament_details_view(request, tournament_id):
    """
    Displays details of a specific tournament for viewers.
    This view reuses much of the logic from adminpanel.views.tournament_details_view.
    """
    tournament = get_object_or_404(Tournament, id=tournament_id) # No created_by check as it's for all viewers
    
    # Get all teams in the tournament
    teams_queryset = tournament.teams.all()

    # Initialize points table (all points to zero initially)
    points_table = []
    for team in teams_queryset:
        points_table.append({
            'team_id': team.id,
            'team_name': team.name,
            'points': 0, # Starting points
            'matches_played': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
        })
    points_table.sort(key=lambda x: x['team_name']) 

    # Get all games associated with this tournament
    tournament_games = tournament.games.all()

    # Get all matches for this tournament, grouped by game
    matches_by_game_data = {}
    for game in tournament_games:
        matches_data = Match.objects.filter(tournament=tournament, game=game).order_by('match_number').values(
            'id', 'match_number', 'score_team1', 'score_team2', 'team1__id', 'team1__name', 'team2__id', 'team2__name'
        )
        matches_by_game_data[game.name] = list(matches_data)

    matches_by_game_json = json.dumps(matches_by_game_data)

    return render(request, 'tournament_details.html', { # REUSING THE ADMIN TEMPLATE
        'tournament': tournament,
        'points_table': points_table,
        'tournament_games': tournament_games,
        'matches_by_game': matches_by_game_json,
        # No 'messages' context for viewer, as they don't configure matches here
    })

