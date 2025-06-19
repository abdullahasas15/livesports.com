# livesports_project/apps/adminpanel/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages # For showing success/error messages
from django.db import transaction # Import transaction for atomic operations

from .forms import AdminSignUpForm, AdminLoginForm, TournamentCreationForm
from apps.tournaments.models import Tournament, Team # Ensure correct import path for Tournament and Team models

def admin_login_signup(request):
    """
    Handles both admin login and signup requests.
    If a GET request, displays the forms.
    If a POST request, processes either login or signup.
    """
    if request.user.is_authenticated:
        # If already logged in, redirect to dashboard
        return redirect('adminpanel:dashboard')

    login_form = AdminLoginForm()
    signup_form = AdminSignUpForm()
    
    if request.method == 'POST':
        # Determine which form was submitted based on the button name or a hidden field
        if 'login_submit' in request.POST:
            login_form = AdminLoginForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f"Welcome back, {username}!")
                    # Check if the user has created any tournaments
                    if Tournament.objects.filter(created_by=user).exists():
                        return redirect('adminpanel:dashboard')
                    else:
                        # If no tournaments, redirect to create their first one
                        return redirect('adminpanel:create_tournament')
                else:
                    messages.error(request, "Invalid username or password.")
            # If login_form is invalid, it will fall through to the final render

        elif 'signup_submit' in request.POST:
            signup_form = AdminSignUpForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                # Log the user in immediately after successful signup
                login(request, user)
                messages.success(request, f"Account created for {user.username}! Please create your first tournament.")
                return redirect('adminpanel:create_tournament')
            # If signup_form is invalid, it will fall through to the final render
        
        # This single return statement handles re-rendering the forms with errors for both login and signup
        return render(request, 'login_signup.html', {
            'login_form': login_form,
            'signup_form': signup_form,
        })

    # For GET request or initial load, render empty forms
    return render(request, 'login_signup.html', {
        'login_form': login_form,
        'signup_form': signup_form,
    })

@login_required # Ensures only logged-in users can access this view
def create_tournament_view(request):
    """
    Handles displaying and processing the tournament creation form, including teams.
    """
    if request.method == 'POST':
        form = TournamentCreationForm(request.POST)
        if form.is_valid():
            num_teams = form.cleaned_data['num_teams']
            team_names = []
            
            # Manually collect team names from POST data and validate them
            for i in range(1, num_teams + 1):
                team_name = request.POST.get(f'team_name_{i}', '').strip()
                if not team_name:
                    # If any team name is empty, add a form error and re-render
                    messages.error(request, f"Team {i} name cannot be empty. Please fill all team name fields.")
                    # Re-render form with submitted data to preserve other fields
                    return render(request, 'create_tournament.html', {'form': form})
                team_names.append(team_name) # <--- CORRECTED LINE: Changed 'name' to 'team_name'
            
            # Use a transaction for atomic creation of tournament and teams
            try:
                with transaction.atomic():
                    tournament = form.save(commit=False) # Don't save Tournament yet
                    tournament.created_by = request.user # Link tournament to current user
                    tournament.save() # Save the Tournament instance
                    form.save_m2m() # Save ManyToMany relations (games)

                    # Create and save Team instances
                    for name in team_names: # 'name' here is iterating over items in team_names list
                        # Add a check for duplicate team names within the current submission
                        # Although unique_together is in model, this provides immediate feedback
                        if Team.objects.filter(tournament=tournament, name=name).exists():
                            raise ValueError(f"Team '{name}' already exists in this tournament.")
                        Team.objects.create(tournament=tournament, name=name)

                messages.success(request, f"Tournament '{tournament.name}' and {len(team_names)} teams created successfully!")
                return redirect('adminpanel:dashboard') # Redirect to dashboard after creation
            except ValueError as e: # Catch custom ValueError for duplicate team names
                messages.error(request, str(e)) # Display the specific error message
                return render(request, 'create_tournament.html', {'form': form})
            except Exception as e: # Catch any other unexpected database or server errors
                messages.error(request, f"An unexpected error occurred: {e}")
                # Re-render form with current data in case of unexpected errors
                return render(request, 'create_tournament.html', {'form': form})
        else:
            # If main form (tournament name, date, games, num_teams) is invalid
            messages.error(request, "Please correct the errors in the tournament form.")
    else:
        form = TournamentCreationForm() # An empty form for GET request

    return render(request, 'create_tournament.html', {'form': form})

@login_required
def admin_dashboard_view(request):
    """
    Displays all tournaments created by the currently logged-in admin.
    """
    # Fetch tournaments created by the current user
    tournaments = Tournament.objects.filter(created_by=request.user).order_by('-start_date')
    
    return render(request, 'admin_dashboard.html', {'tournaments': tournaments})

def admin_logout_view(request):
    """
    Logs out the admin and redirects to the login page.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('adminpanel:login_signup')
