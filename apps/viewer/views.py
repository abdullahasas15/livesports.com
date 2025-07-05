# livesports_project/apps/viewer/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json

from apps.tournaments.models import Tournament, Team, Game, Match, UserProfile
from .forms import ViewerSignUpForm 
from apps.adminpanel.forms import AdminLoginForm # CORRECTED IMPORT PATH: from apps.adminpanel.forms

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
        matches_as_team1 = tournament.matches.filter(team1=team, status='completed')
        matches_as_team2 = tournament.matches.filter(team2=team, status='completed')
        total_points = sum(m.points_team1 for m in matches_as_team1) + sum(m.points_team2 for m in matches_as_team2)
        matches_played = matches_as_team1.count() + matches_as_team2.count()
        wins = 0
        losses = 0
        draws = 0
        for m in matches_as_team1:
            if m.points_team1 > m.points_team2:
                wins += 1
            elif m.points_team1 < m.points_team2:
                losses += 1
            else:
                draws += 1
        for m in matches_as_team2:
            if m.points_team2 > m.points_team1:
                wins += 1
            elif m.points_team2 < m.points_team1:
                losses += 1
            else:
                draws += 1
        points_table.append({
            'team_id': team.id,
            'team_name': team.name,
            'points': total_points,
            'matches_played': matches_played,
            'wins': wins,
            'losses': losses,
            'draws': draws,
        })
    points_table.sort(key=lambda x: (-x['points'], -x['wins'], x['team_name']))

    tournament_games = tournament.games.all()

    matches_by_game_data = {}
    for game in tournament_games:
        matches_data = Match.objects.filter(tournament=tournament, game=game).order_by('match_number').values(
            'id', 'match_number', 'score_team1', 'score_team2', 'total_points',
            'status', 'winner__name', 'team1__id', 'team1__name', 'team2__id', 'team2__name',
            'player1_team1', 'player2_team1', 'player1_team2', 'player2_team2','description'
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
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('home:home')

    if request.method == 'POST':
        form = ViewerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect('viewer:tournament_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ViewerSignUpForm()
    
    return render(request, 'viewer_signup.html', {'form': form})


def viewer_login_view(request):
    """
    Handles viewer login. Reuses AdminLoginForm for authentication.
    """
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('viewer:tournament_list')

    login_form = AdminLoginForm()

    if request.method == 'POST':
        login_form = AdminLoginForm(request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('viewer:tournament_list') 
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors in the login form.")
    
    return render(request, 'viewer_login.html', {
        'login_form': login_form,
        'is_viewer_login_page': True
    })

@login_required
def viewer_profile_view(request):
    user_profile = request.user.userprofile 
    
    return render(request, 'viewer_profile.html', {
        'user': request.user,
        'profile': user_profile,
    })
