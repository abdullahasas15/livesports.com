# adminpanel/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages # For showing success/error messages

from .forms import AdminSignUpForm, AdminLoginForm, TournamentCreationForm
from apps.tournaments.models import Tournament # Ensure correct import path for Tournament model

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
            else:
                # Form is invalid, but try to be specific for user feedback
                messages.error(request, "Please correct the errors in the login form.")

        elif 'signup_submit' in request.POST:
            signup_form = AdminSignUpForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                # Log the user in immediately after successful signup
                login(request, user)
                messages.success(request, f"Account created for {user.username}! Please create your first tournament.")
                return redirect('adminpanel:create_tournament')
            else:
                # Form is invalid, pass errors back to template
                messages.error(request, "Please correct the errors in the signup form.")
        
        # If any form was submitted and had errors, re-render with context
        return render(request, 'login_signup.html', {
            'login_form': login_form,
            'signup_form': signup_form,
        })

    # For GET request or initial load
    # adminpanel/views.py (inside admin_login_signup view, just before the final return render)
    print("Signup Form Fields:", signup_form.fields.keys())
# ... rest of the view ...
    return render(request, 'login_signup.html', {
    'login_form': login_form,
    'signup_form': signup_form,
})
    return render(request, 'login_signup.html', {
        'login_form': login_form,
        'signup_form': signup_form,
    })

@login_required # Ensures only logged-in users can access this view
def create_tournament_view(request):
    """
    Handles displaying and processing the tournament creation form.
    """
    # Check if the user is an admin (e.g., is_staff or is_superuser) if you have such a requirement.
    # For now, any logged-in user can create a tournament.

    if request.method == 'POST':
        form = TournamentCreationForm(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False) # Don't save to DB yet
            tournament.created_by = request.user # Link tournament to current user
            tournament.save() # Save the tournament instance
            
            # Save ManyToMany relations (games) after the tournament instance is saved
            form.save_m2m() # This is crucial for ManyToManyField (like 'games')

            messages.success(request, f"Tournament '{tournament.name}' created successfully!")
            return redirect('adminpanel:dashboard') # Redirect to dashboard after creation
        else:
            messages.error(request, "Please correct the errors below.")
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

