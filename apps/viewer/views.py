# livesports_project/apps/viewer/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json

from apps.tournaments.models import Tournament, Team, Game, Match, UserProfile
from .forms import ViewerSignUpForm

def viewer_tournament_list_view(request):
    query = request.GET.get('q')
    
    if query:
        tournaments = Tournament.objects.filter(
            Q(name__icontains=query) | 
            Q(games__name__icontains=query)
        ).distinct().order_by('-start_date')
    else:
        tournaments = Tournament.objects.all().order_by('-start_date')
    
    return render(request, 'viewer_tournament_list.html', {
        'tournaments': tournaments,
        'query': query,
    })


def viewer_tournament_details_view(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    teams_queryset = tournament.teams.all()

    points_table = []
    for team in teams_queryset:
        points_table.append({
            'team_id': team.id,
            'team_name': team.name,
            'points': 0,
            'matches_played': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
        })
    points_table.sort(key=lambda x: x['team_name']) 

    tournament_games = tournament.games.all()

    matches_by_game_data = {}
    for game in tournament_games:
        matches_data = Match.objects.filter(tournament=tournament, game=game).order_by('match_number').values(
            'id', 'match_number', 'score_team1', 'score_team2', 'team1__id', 'team1__name', 'team2__id', 'team2__name'
        )
        matches_by_game_data[game.name] = list(matches_data)

    matches_by_game_json = json.dumps(matches_by_game_data)

    return render(request, 'tournament_details.html', {
        'tournament': tournament,
        'points_table': points_table,
        'tournament_games': tournament_games,
        'matches_by_game': matches_by_game_json,
    })

def viewer_signup_view(request):
    """
    Handles viewer signup.
    """
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('home:home') # This redirect is fine if user is ALREADY logged in

    if request.method == 'POST':
        form = ViewerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            # CORRECTED REDIRECTION for new viewer signup:
            return redirect('viewer:tournament_list') # Redirect to viewer tournament list
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ViewerSignUpForm()
    
    return render(request, 'viewer_signup.html', {'form': form})

@login_required
def viewer_profile_view(request):
    """
    Displays the logged-in viewer's profile information.
    """
    user_profile = request.user.userprofile 
    
    return render(request, 'viewer_profile.html', {
        'user': request.user,
        'profile': user_profile,
    })

