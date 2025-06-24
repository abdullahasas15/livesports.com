# livesports_project/apps/adminpanel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError
import json

from .forms import AdminSignUpForm, AdminLoginForm, TournamentCreationForm
from apps.tournaments.models import Tournament, Team, Game, Match

# Renamed from admin_login_signup to user_auth_view for generic use
def user_auth_view(request):
    """
    Handles both user login and signup requests for both admins and viewers.
    If a GET request, displays the forms.
    If a POST request, processes either login or signup.
    """
    if request.user.is_authenticated:
        # Redirect based on user type after login
        if request.user.is_staff:
            return redirect('adminpanel:dashboard')
        else:
            return redirect('viewer:tournament_list') # Viewers go to tournament list after login

    login_form = AdminLoginForm() # Reusing AdminLoginForm, as it's a standard AuthenticationForm
    signup_form = AdminSignUpForm() # This is the form that sets is_staff=True

    # We also need a generic signup form for viewers that does NOT set is_staff=True
    # This implies we might need two signup forms in the context, or dynamically choose one.
    # For now, if we get a signup_submit from this page, it will be an AdminSignUpForm.
    # We will provide a separate viewer signup page and not use signup from here for viewers.

    # If the request method is POST, process the submitted form
    if request.method == 'POST':
        if 'login_submit' in request.POST:
            login_form = AdminLoginForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f"Welcome back, {username}!")
                    # Redirect based on user type after login
                    if user.is_staff:
                        return redirect('adminpanel:dashboard')
                    else:
                        return redirect('viewer:tournament_list') # Viewers go to tournament list after login
                else:
                    messages.error(request, "Invalid username or password.")
            # If login_form is invalid, it falls through to the final render
        
        # Note: Signups on THIS page are assumed to be Admin signups.
        # Viewer signups happen on the dedicated viewer:signup page.
        elif 'signup_submit' in request.POST:
            signup_form = AdminSignUpForm(request.POST) # This form sets is_staff=True
            if signup_form.is_valid():
                user = signup_form.save() # User will have is_staff=True
                login(request, user)
                messages.success(request, f"Account created for {user.username}! Welcome to the Admin Panel.")
                return redirect('adminpanel:create_tournament') # Admins create their first tournament
            else:
                messages.error(request, "Please correct the errors in the signup form.")
        
        # Render the form again with errors if any
        return render(request, 'login_signup.html', {
            'login_form': login_form,
            'signup_form': signup_form, # This is AdminSignUpForm
            'is_admin_login_page': True # Flag for template to show Admin specific branding
        })

    # For GET request or initial load
    return render(request, 'login_signup.html', {
        'login_form': login_form,
        'signup_form': signup_form, # This is AdminSignUpForm
        'is_admin_login_page': True # Flag for template to show Admin specific branding
    })

@login_required
def create_tournament_view(request):
    if request.method == 'POST':
        form = TournamentCreationForm(request.POST)
        if form.is_valid():
            num_teams = form.cleaned_data['num_teams']
            team_names = []
            
            for i in range(1, num_teams + 1):
                team_name = request.POST.get(f'team_name_{i}', '').strip()
                if not team_name:
                    messages.error(request, f"Team {i} name cannot be empty. Please fill all team name fields.")
                    return render(request, 'create_tournament.html', {'form': form})
                team_names.append(team_name)
            
            try:
                with transaction.atomic():
                    tournament = form.save(commit=False)
                    tournament.created_by = request.user
                    tournament.save()
                    form.save_m2m()

                    for name in team_names:
                        if Team.objects.filter(tournament=tournament, name=name).exists():
                            raise ValueError(f"Team '{name}' already exists in this tournament.")
                        Team.objects.create(tournament=tournament, name=name)

                messages.success(request, f"Tournament '{tournament.name}' and {len(team_names)} teams created successfully! Now, configure matches for this tournament.")
                return redirect('adminpanel:manage_matches', tournament_id=tournament.id)
            except ValueError as e:
                messages.error(request, str(e))
                return render(request, 'create_tournament.html', {'form': form})
            except IntegrityError as e:
                messages.error(request, "A database error occurred, possibly a duplicate team name or other unique constraint violation. Please check team names.")
                return render(request, 'create_tournament.html', {'form': form})
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
                return render(request, 'create_tournament.html', {'form': form})
        else:
            messages.error(request, "Please correct the errors in the tournament form.")
    else:
        form = TournamentCreationForm()

    return render(request, 'create_tournament.html', {'form': form})

@login_required
def admin_dashboard_view(request):
    tournaments = Tournament.objects.filter(created_by=request.user).order_by('-start_date')
    return render(request, 'admin_dashboard.html', {'tournaments': tournaments})

@login_required
def manage_matches_view(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id, created_by=request.user)
    
    tournament_games = tournament.games.all()
    tournament_teams_queryset = tournament.teams.all()
    tournament_teams_data = [{'id': team.id, 'name': team.name} for team in tournament_teams_queryset]
    tournament_teams_json = json.dumps(tournament_teams_data)

    existing_matches_by_game_data = {}
    for game in tournament_games:
        matches = Match.objects.filter(tournament=tournament, game=game).order_by('match_number')
        if matches.exists():
            matches_list = []
            for match in matches:
                matches_list.append({
                    'match_number': match.match_number,
                    'team1Id': match.team1.id,
                    'team2Id': match.team2.id,
                })
            existing_matches_by_game_data[game.id] = {
                'numMatches': matches.count(),
                'matches': matches_list
            }
    existing_matches_by_game_json = json.dumps(existing_matches_by_game_data)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                for game in tournament_games:
                    num_matches_key = f'num_matches_{game.id}'
                    num_matches = int(request.POST.get(num_matches_key, 0))

                    if num_matches < 0:
                        raise ValueError(f"Number of matches for {game.name} cannot be negative.")

                    Match.objects.filter(tournament=tournament, game=game).delete()

                    for i in range(1, num_matches + 1):
                        team1_key = f'game_{game.id}_match_{i}_team1'
                        team2_key = f'game_{game.id}_match_{i}_team2'
                        
                        team1_id = request.POST.get(team1_key)
                        team2_id = request.POST.get(team2_key)

                        if not team1_id or not team2_id:
                            raise ValueError(f"Please select both teams for Match {i} of {game.name}.")
                        
                        team1 = get_object_or_404(Team, id=team1_id, tournament=tournament)
                        team2 = get_object_or_404(Team, id=team2_id, tournament=tournament)

                        if team1 == team2:
                            raise ValueError(f"Team 1 and Team 2 cannot be the same for Match {i} of {game.name}.")

                        Match.objects.create(
                            tournament=tournament,
                            game=game,
                            match_number=i,
                            team1=team1,
                            team2=team2
                        )
            messages.success(request, f"Matches for tournament '{tournament.name}' configured successfully!")
            return redirect('adminpanel:matches_configured')
        except ValueError as e:
            messages.error(request, str(e))
        except IntegrityError as e:
            messages.error(request, "A database error occurred, possibly a duplicate match configuration. Please check your inputs.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
        
        return render(request, 'manage_matches.html', {
            'tournament': tournament,
            'tournament_games': tournament_games,
            'tournament_teams': tournament_teams_json,
            'existing_matches_by_game': existing_matches_by_game_json,
        })
    
    return render(request, 'manage_matches.html', {
        'tournament': tournament,
        'tournament_games': tournament_games,
        'tournament_teams': tournament_teams_json,
        'existing_matches_by_game': existing_matches_by_game_json,
    })

@login_required
def tournament_details_view(request, tournament_id):
    """
    Displays details of a specific tournament, including points table and matches per game.
    """
    tournament = get_object_or_404(Tournament, id=tournament_id, created_by=request.user)
    
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

@login_required
def add_more_matches_view(request, tournament_id, game_id):
    tournament = get_object_or_404(Tournament, id=tournament_id, created_by=request.user)
    game = get_object_or_404(Game, id=game_id)
    
    tournament_teams_queryset = tournament.teams.all()
    tournament_teams_json = json.dumps([{'id': team.id, 'name': team.name} for team in tournament_teams_queryset])

    existing_matches = Match.objects.filter(tournament=tournament, game=game).order_by('match_number')
    
    initial_num_matches = existing_matches.count()
    existing_match_data = []
    for match in existing_matches:
        existing_match_data.append({
            'match_number': match.match_number,
            'team1Id': match.team1.id,
            'team2Id': match.team2.id,
        })

    if request.method == 'POST':
        num_matches_key = f'num_matches_{game.id}'
        num_matches = int(request.POST.get(num_matches_key, 0))
        
        new_match_data_list = []
        for i in range(1, num_matches + 1):
            team1_key = f'game_{game.id}_match_{i}_team1'
            team2_key = f'game_{game.id}_match_{i}_team2'
            
            team1_id = request.POST.get(team1_key)
            team2_id = request.POST.get(team2_key)

            if not team1_id or not team2_id:
                messages.error(request, f"Please select both teams for Match {i}.")
                context = {
                    'tournament': tournament,
                    'game': game,
                    'tournament_teams': tournament_teams_json,
                    'initial_num_matches': num_matches,
                    'existing_match_data': json.dumps([
                        {'match_number': i, 'team1Id': team1_id, 'team2Id': team2_id} 
                        for i in range(1, num_matches + 1)
                    ]),
                    'is_adding_new_matches': True,
                }
                return render(request, 'add_more_matches.html', context)
            
            new_match_data_list.append({
                'match_number': i,
                'team1_id': team1_id,
                'team2_id': team2_id,
            })
        
        try:
            with transaction.atomic():
                current_max_match_number = Match.objects.filter(tournament=tournament, game=game).count()
                
                for new_match_info in new_match_data_list:
                    match_number_to_add = current_max_match_number + new_match_info['match_number']
                    
                    team1 = get_object_or_404(Team, id=new_match_info['team1_id'], tournament=tournament)
                    team2 = get_object_or_404(Team, id=new_match_info['team2_id'], tournament=tournament)

                    if team1 == team2:
                        raise ValueError(f"Team 1 and Team 2 cannot be the same for Match {new_match_info['match_number']}.")

                    Match.objects.create(
                        tournament=tournament,
                        game=game,
                        match_number=match_number_to_add,
                        team1=team1,
                        team2=team2
                    )
            messages.success(request, f"{num_matches} additional matches configured for {game.name}!")
            return redirect('adminpanel:tournament_details', tournament_id=tournament.id)
        except ValueError as e:
            messages.error(request, str(e))
        except IntegrityError as e:
            messages.error(request, "A database error occurred, possibly a duplicate match configuration. Please check your inputs.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
        
        context = {
            'tournament': tournament,
            'game': game,
            'tournament_teams': tournament_teams_json,
            'initial_num_matches': num_matches,
            'existing_match_data': json.dumps(new_match_data_list),
            'is_adding_new_matches': True,
        }
        return render(request, 'add_more_matches.html', context)
    
    context = {
        'tournament': tournament,
        'game': game,
        'tournament_teams': tournament_teams_json,
        'initial_num_matches': existing_matches.count() + 1 if existing_matches.exists() else 1, # Start with current count + 1 or 1
        'existing_match_data': json.dumps(existing_match_data), # Existing matches for pre-population
        'is_adding_new_matches': True,
    }
    return render(request, 'add_more_matches.html', context)


@login_required
def matches_configured_view(request):
    return render(request, 'matches_configured.html')

def admin_logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('adminpanel:login_signup')
