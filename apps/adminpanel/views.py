# livesports_project/apps/adminpanel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError
import json

from .forms import AdminSignUpForm, AdminLoginForm, TournamentCreationForm
from apps.tournaments.models import Tournament, Team, Game, Match 

def user_auth_view(request):
    """
    Handles both user login and signup requests for admins.
    Superusers are redirected to the main Django admin login.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('adminpanel:dashboard')
        else:
            return redirect('viewer:tournament_list')

    login_form = AdminLoginForm() 
    signup_form = AdminSignUpForm() 

    if request.method == 'POST':
        if 'login_submit' in request.POST:
            login_form = AdminLoginForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_superuser:
                        messages.error(request, "Superusers must log in via the main Django admin site.")
                        return redirect('admin:index')
                        
                    login(request, user)
                    messages.success(request, f"Welcome back, {username}!")
                    
                    if user.is_staff:
                        if Tournament.objects.filter(created_by=user).exists():
                            return redirect('adminpanel:dashboard')
                        else:
                            return redirect('adminpanel:create_tournament')
                    else:
                        messages.warning(request, "You logged in, but you don't have admin privileges. Redirecting to viewer tournaments.")
                        return redirect('viewer:tournament_list') 
                else:
                    messages.error(request, "Invalid username or password.")
        
        elif 'signup_submit' in request.POST:
            signup_form = AdminSignUpForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                messages.success(request, f"Admin account created for {user.username}! Welcome to the Admin Panel.")
                return redirect('adminpanel:create_tournament')
            else:
                messages.error(request, "Please correct the errors in the signup form.")
        
        return render(request, 'login_signup.html', {
            'login_form': login_form,
            'signup_form': signup_form,
            'is_admin_login_page': True 
        })

    return render(request, 'login_signup.html', {
        'login_form': login_form,
        'signup_form': signup_form,
        'is_admin_login_page': True 
    })

@login_required
def create_tournament_view(request):
    if request.user.is_superuser:
        messages.error(request, "Superusers cannot create tournaments via this interface. Please use the main Django Admin site for core data management if needed.")
        return redirect('adminpanel:dashboard')
        
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to create tournaments.")
        return redirect('home:home')

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
                            raise ValueError(f"Team '{name}' already exists in this tournament. Please use unique team names.")
                        Team.objects.create(tournament=tournament, name=name)

                messages.success(request, f"Tournament '{tournament.name}' and {len(team_names)} teams created successfully! Now, configure matches for this tournament.")
                return redirect('adminpanel:manage_matches', tournament_id=tournament.id) 
            except ValueError as e:
                messages.error(request, str(e))
                return render(request, 'create_tournament.html', {'form': form})
            except IntegrityError as e:
                messages.error(request, "A database error occurred, possibly a duplicate entry. Please check your inputs.")
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
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to view the admin dashboard.")
        return redirect('home:home')

    tournaments = Tournament.objects.filter(created_by=request.user).order_by('-start_date')
    return render(request, 'admin_dashboard.html', {'tournaments': tournaments})

@login_required
def manage_matches_view(request, tournament_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to manage matches.")
        return redirect('home:home')

    tournament = get_object_or_404(Tournament, id=tournament_id, created_by=request.user)
    
    tournament_games = tournament.games.all()
    tournament_teams_queryset = tournament.teams.all()
    tournament_teams_data = [{'id': team.id, 'name': team.name} for team in tournament_teams_queryset]
    tournament_teams_json = json.dumps(tournament_teams_data)

    existing_matches_by_game_data = {}
    for game_obj in tournament_games: 
        matches = Match.objects.filter(tournament=tournament, game=game_obj).order_by('match_number')
        if matches.exists():
            matches_list = []
            for match in matches:
                match_data = {
                    'match_number': match.match_number,
                    'team1Id': match.team1.id,
                    'team2Id': match.team2.id,
                }
                if game_obj.name == 'Badminton':
                    match_data['totalPoints'] = match.total_points
                    match_data['player1Team1Name'] = match.player1_team1
                    match_data['player2Team1Name'] = match.player2_team1
                    match_data['player1Team2Name'] = match.player1_team2
                    match_data['player2Team2Name'] = match.player2_team2
                matches_list.append(match_data)
            existing_matches_by_game_data[game_obj.id] = {
                'numMatches': matches.count(),
                'matches': matches_list
            }
    existing_matches_by_game_json = json.dumps(existing_matches_by_game_data)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                for game_obj in tournament_games: 
                    num_matches_key = f'num_matches_{game_obj.id}'
                    num_matches = int(request.POST.get(num_matches_key, 0))

                    if num_matches < 0:
                        raise ValueError(f"Number of matches for {game_obj.name} cannot be negative.")

                    # Only add new matches, do not delete existing ones
                    existing_match_numbers = set(
                        Match.objects.filter(tournament=tournament, game=game_obj).values_list('match_number', flat=True)
                    )
                    next_match_number = max(existing_match_numbers) + 1 if existing_match_numbers else 1

                    for i in range(1, num_matches + 1):
                        team1_key = f'game_{game_obj.id}_match_{i}_team1'
                        team2_key = f'game_{game_obj.id}_match_{i}_team2'
                        
                        team1_id = request.POST.get(team1_key)
                        team2_id = request.POST.get(team2_key)
                        
                        total_points_val = None 
                        player1_team1_name = '' 
                        player2_team1_name = '' 
                        player1_team2_name = '' 
                        player2_team2_name = '' 
                        
                        if game_obj.name == 'Badminton':
                            total_points_key = f'game_{game_obj.id}_match_{i}_total_points'
                            player1_team1_name_key = f'game_{game_obj.id}_match_{i}_player1_team1_name'
                            player2_team1_name_key = f'game_{game_obj.id}_match_{i}_player2_team1_name'
                            player1_team2_name_key = f'game_{game_obj.id}_match_{i}_player1_team2_name'
                            player2_team2_name_key = f'game_{game_obj.id}_match_{i}_player2_team2_name'

                            total_points_val = request.POST.get(total_points_key)
                            player1_team1_name = request.POST.get(player1_team1_name_key, '').strip()
                            player2_team1_name = request.POST.get(player2_team1_name_key, '').strip()
                            player1_team2_name = request.POST.get(player1_team2_name_key, '').strip()
                            player2_team2_name = request.POST.get(player2_team2_name_key, '').strip()

                            if not total_points_val or not total_points_val.isdigit() or not (1 <= int(total_points_val) <= 99):
                                raise ValueError(f"Please enter a valid number of points (1-99) for Match {i} of {game_obj.name}.")
                            total_points_val = int(total_points_val)

                            if not player1_team1_name and not player2_team1_name:
                                raise ValueError(f"Please enter at least one player name for Team 1 in Match {i} of {game_obj.name}.")
                            if not player1_team2_name and not player2_team2_name:
                                raise ValueError(f"Please enter at least one player name for Team 2 in Match {i} of {game_obj.name}.")

                            if player1_team1_name and player2_team1_name and player1_team1_name == player2_team1_name:
                                raise ValueError(f"Player 1 and Player 2 names for Team 1 cannot be the same in Match {i} of {game_obj.name}.")
                            if player1_team2_name and player2_team2_name and player1_team2_name == player2_team2_name:
                                raise ValueError(f"Player 1 and Player 2 names for Team 2 cannot be the same in Match {i} of {game_obj.name}.")

                        if not team1_id or not team2_id:
                            raise ValueError(f"Please select both teams for Match {i} of {game_obj.name}.")
                        
                        team1 = get_object_or_404(Team, id=team1_id, tournament=tournament)
                        team2 = get_object_or_404(Team, id=team2_id, tournament=tournament)

                        if team1 == team2:
                            raise ValueError(f"Team 1 and Team 2 cannot be the same for Match {i} of {game_obj.name}.")

                        match_kwargs = {
                            'tournament': tournament,
                            'game': game_obj,
                            'match_number': next_match_number,
                            'team1': team1,
                            'team2': team2,
                        }
                        next_match_number += 1
                        if total_points_val is not None:
                            match_kwargs['total_points'] = total_points_val
                        if player1_team1_name:
                            match_kwargs['player1_team1'] = player1_team1_name
                        if player2_team1_name:
                            match_kwargs['player2_team1'] = player2_team1_name
                        if player1_team2_name:
                            match_kwargs['player1_team2'] = player1_team2_name
                        if player2_team2_name:
                            match_kwargs['player2_team2'] = player2_team2_name
                        
                        Match.objects.create(**match_kwargs)
            messages.success(request, f"Matches for tournament '{tournament.name}' configured successfully!")
            return redirect('adminpanel:matches_configured')
        except ValueError as e:
            messages.error(request, str(e))
            # Re-render the form with error and previous inputs
            re_rendered_existing_matches_by_game = {}
            for game_obj_r in tournament_games:
                num_matches_r = int(request.POST.get(f'num_matches_{game_obj_r.id}', 0))
                matches_r = []
                for i in range(1, num_matches_r + 1):
                    team1_id_r = request.POST.get(f'game_{game_obj_r.id}_match_{i}_team1')
                    team2_id_r = request.POST.get(f'game_{game_obj_r.id}_match_{i}_team2')
                    total_points_r = None
                    player1_team1_name_r = ''
                    player2_team1_name_r = ''
                    player1_team2_name_r = ''
                    player2_team2_name_r = ''

                    if game_obj_r.name == 'Badminton':
                        total_points_r = request.POST.get(f'game_{game_obj_r.id}_match_{i}_total_points')
                        player1_team1_name_r = request.POST.get(f'game_{game_obj_r.id}_match_{i}_player1_team1_name', '').strip()
                        player2_team1_name_r = request.POST.get(f'game_{game_obj_r.id}_match_{i}_player2_team1_name', '').strip()
                        player1_team2_name_r = request.POST.get(f'game_{game_obj_r.id}_match_{i}_player1_team2_name', '').strip()
                        player2_team2_name_r = request.POST.get(f'game_{game_obj_r.id}_match_{i}_player2_team2_name', '').strip()
                    
                    matches_r.append({
                        'match_number': i,
                        'team1Id': team1_id_r,
                        'team2Id': team2_id_r,
                        'totalPoints': total_points_r,
                        'player1Team1Name': player1_team1_name_r,
                        'player2Team1Name': player2_team1_name_r,
                        'player1Team2Name': player1_team2_name_r,
                        'player2Team2Name': player2_team2_name_r,
                    })
                re_rendered_existing_matches_by_game[game_obj_r.id] = {
                    'numMatches': num_matches_r,
                    'matches': matches_r
                }
            return render(request, 'manage_matches.html', {
                'tournament': tournament,
                'tournament_games': tournament_games,
                'tournament_teams': tournament_teams_json,
                'existing_matches_by_game': json.dumps(re_rendered_existing_matches_by_game),
            })
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
            'id', 'match_number', 'score_team1', 'score_team2', 'total_points',
            'status', 'winner__name', 'team1__id', 'team1__name', 'team2__id', 'team2__name',
            'player1_team1', 'player2_team1', 'player1_team2', 'player2_team2'
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
    # Ensure only staff can add matches
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to add matches.")
        return redirect('home:home')

    tournament = get_object_or_404(Tournament, id=tournament_id, created_by=request.user)
    game = get_object_or_404(Game, id=game_id)
    
    tournament_teams_queryset = tournament.teams.all()
    tournament_teams_json = json.dumps([{'id': team.id, 'name': team.name} for team in tournament_teams_queryset])

    existing_matches = Match.objects.filter(tournament=tournament, game=game).order_by('match_number')
    existing_match_data = []
    for match in existing_matches:
        match_data = {
            'match_number': match.match_number,
            'team1Id': match.team1.id,
            'team2Id': match.team2.id,
        }
        if game.name == 'Badminton':
            match_data['totalPoints'] = match.total_points
            match_data['player1Team1Name'] = match.player1_team1
            match_data['player2Team1Name'] = match.player2_team1
            match_data['player1Team2Name'] = match.player1_team2
            match_data['player2Team2Name'] = match.player2_team2
        existing_match_data.append(match_data)

    if request.method == 'POST':
        num_matches_key = f'num_matches_{game.id}'
        num_matches = int(request.POST.get(num_matches_key, 0))
        
        new_match_data_list = []
        for i in range(1, num_matches + 1):
            team1_key = f'game_{game.id}_match_{i}_team1'
            team2_key = f'game_{game.id}_match_{i}_team2'
            
            team1_id = request.POST.get(team1_key)
            team2_id = request.POST.get(team2_key)
            
            total_points_val = None 
            player1_team1_name = '' 
            player2_team1_name = '' 
            player1_team2_name = '' 
            player2_team2_name = '' 
            
            if game.name == 'Badminton':
                total_points_key = f'game_{game.id}_match_{i}_total_points'
                player1_team1_name_key = f'game_{game.id}_match_{i}_player1_team1_name'
                player2_team1_name_key = f'game_{game.id}_match_{i}_player2_team1_name'
                player1_team2_name_key = f'game_{game.id}_match_{i}_player1_team2_name'
                player2_team2_name_key = f'game_{game.id}_match_{i}_player2_team2_name'

                total_points_val = request.POST.get(total_points_key)
                player1_team1_name = request.POST.get(player1_team1_name_key, '').strip()
                player2_team1_name = request.POST.get(player2_team1_name_key, '').strip()
                player1_team2_name = request.POST.get(player1_team2_name_key, '').strip()
                player2_team2_name = request.POST.get(player2_team2_name_key, '').strip()

                if not total_points_val or not total_points_val.isdigit() or not (1 <= int(total_points_val) <= 99):
                    messages.error(request, f"Please enter a valid number of points (1-99) for Match {i} of {game.name}.")
                    context = {
                        'tournament': tournament, 'game': game, 'tournament_teams': tournament_teams_json,
                        'initial_num_matches': num_matches, 'existing_match_data': json.dumps([
                            {'match_number': i, 'team1Id': team1_id, 'team2Id': team2_id, 'totalPoints': total_points_val, 
                             'player1Team1Name': player1_team1_name, 'player2Team1Name': player2_team1_name,
                             'player1Team2Name': player1_team2_name, 'player2Team2Name': player2_team2_name}
                            for i in range(1, num_matches + 1)
                        ]), 'is_adding_new_matches': True,
                    }
                    return render(request, 'add_more_matches.html', context)
                total_points_val = int(total_points_val)

                if not player1_team1_name and not player2_team1_name:
                    messages.error(request, f"Please enter at least one player name for Team 1 in Match {i} of {game.name}.")
                    context = {
                        'tournament': tournament, 'game': game, 'tournament_teams': tournament_teams_json,
                        'initial_num_matches': num_matches, 'existing_match_data': json.dumps([
                            {'match_number': i, 'team1Id': team1_id, 'team2Id': team2_id, 'totalPoints': total_points_val, 
                             'player1Team1Name': player1_team1_name, 'player2Team1Name': player2_team1_name,
                             'player1Team2Name': player1_team2_name, 'player2Team2Name': player2_team2_name}
                            for i in range(1, num_matches + 1)
                        ]), 'is_adding_new_matches': True,
                    }
                    return render(request, 'add_more_matches.html', context)
                if not player1_team2_name and not player2_team2_name:
                    messages.error(request, f"Please enter at least one player name for Team 2 in Match {i} of {game.name}.")
                    context = {
                        'tournament': tournament, 'game': game, 'tournament_teams': tournament_teams_json,
                        'initial_num_matches': num_matches, 'existing_match_data': json.dumps([
                            {'match_number': i, 'team1Id': team1_id, 'team2Id': team2_id, 'totalPoints': total_points_val, 
                             'player1Team1Name': player1_team1_name, 'player2Team1Name': player2_team1_name,
                             'player1Team2Name': player1_team2_name, 'player2Team2Name': player2_team2_name}
                            for i in range(1, num_matches + 1)
                        ]), 'is_adding_new_matches': True,
                    }
                    return render(request, 'add_more_matches.html', context)

                if player1_team1_name and player2_team1_name and player1_team1_name == player2_team1_name:
                    raise ValueError(f"Player 1 and Player 2 names for Team 1 cannot be the same in Match {i} of {game.name}.")
                if player1_team2_name and player2_team2_name and player1_team2_name == player2_team2_name:
                    raise ValueError(f"Player 1 and Player 2 names for Team 2 cannot be the same in Match {i} of {game.name}.")

            if not team1_id or not team2_id:
                messages.error(request, f"Please select both teams for Match {i} of {game.name}.")
                context = {
                    'tournament': tournament,
                    'game': game,
                    'tournament_teams': tournament_teams_json,
                    'initial_num_matches': num_matches,
                    'existing_match_data': json.dumps([
                        {'match_number': i, 'team1Id': team1_id, 'team2Id': team2_id, 'totalPoints': total_points_val, 
                         'player1Team1Name': player1_team1_name, 'player2Team1Name': player2_team1_name,
                         'player1Team2Name': player1_team2_name, 'player2Team2Name': player2_team2_name} 
                        for i in range(1, num_matches + 1)
                    ]),
                    'is_adding_new_matches': True,
                }
                return render(request, 'add_more_matches.html', context)
            
            new_match_data_list.append({
                'team1_id': team1_id,
                'team2_id': team2_id,
                'total_points': total_points_val,
                'player1_team1_name': player1_team1_name,
                'player2_team1_name': player2_team1_name,
                'player1_team2_name': player1_team2_name,
                'player2_team2_name': player2_team2_name,
            })
        
        try:
            with transaction.atomic():
                # Find the current max match_number for this game
                existing_match_numbers = set(
                    Match.objects.filter(tournament=tournament, game=game).values_list('match_number', flat=True)
                )
                next_match_number = max(existing_match_numbers) + 1 if existing_match_numbers else 1

                for new_match_info in new_match_data_list:
                    team1 = get_object_or_404(Team, id=new_match_info['team1_id'], tournament=tournament)
                    team2 = get_object_or_404(Team, id=new_match_info['team2_id'], tournament=tournament)

                    if team1 == team2:
                        raise ValueError(f"Team 1 and Team 2 cannot be the same for this match.")

                    match_kwargs = {
                        'tournament': tournament, 'game': game, 'match_number': next_match_number,
                        'team1': team1, 'team2': team2
                    }
                    next_match_number += 1
                    if new_match_info['total_points'] is not None:
                        match_kwargs['total_points'] = new_match_info['total_points']
                    if new_match_info['player1_team1_name']:
                        match_kwargs['player1_team1'] = new_match_info['player1_team1_name']
                    if new_match_info['player2_team1_name']:
                        match_kwargs['player2_team1'] = new_match_info['player2_team1_name']
                    if new_match_info['player1_team2_name']:
                        match_kwargs['player1_team2'] = new_match_info['player1_team2_name']
                    if new_match_info['player2_team2_name']:
                        match_kwargs['player2_team2'] = new_match_info['player2_team2_name']

                    Match.objects.create(**match_kwargs)
            messages.success(request, f"Matches for tournament '{tournament.name}' configured successfully!")
            return redirect('adminpanel:matches_configured')
        except ValueError as e:
            messages.error(request, str(e))
        except IntegrityError as e:
            messages.error(request, "A database error occurred, possibly a duplicate match configuration. Please check your inputs.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
        
        return render(request, 'add_more_matches.html', {
            'tournament': tournament,
            'game': game,
            'tournament_teams': tournament_teams_json,
            'initial_num_matches': num_matches,
            'existing_match_data': json.dumps(new_match_data_list),
            'is_adding_new_matches': True,
        })
    
    context = {
        'tournament': tournament,
        'game': game,
        'tournament_teams': tournament_teams_json,
        'initial_num_matches': existing_matches.count() + 1 if existing_matches.exists() else 1,
        'existing_match_data': json.dumps(existing_match_data),
        'is_adding_new_matches': True,
    }
    return render(request, 'add_more_matches.html', context)

@login_required
def matches_configured_view(request):
    return render(request, 'matches_configured.html')

def admin_logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return