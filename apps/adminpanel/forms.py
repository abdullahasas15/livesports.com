# adminpanel/forms.py
from django import forms
from apps.tournaments.models import Tournament, Game # Ensure correct import path
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# Custom UserCreationForm if you need extra fields for admin signup later
class AdminSignUpForm(UserCreationForm):
    # You can add custom fields here if needed for admin signup
    # For now, it just inherits default username and password
    pass

class AdminLoginForm(AuthenticationForm):
    # This form is for logging in existing users
    pass

class TournamentCreationForm(forms.ModelForm):
    # To display games as checkboxes
    games = forms.ModelMultipleChoiceField(
        queryset=Game.objects.all().order_by('name'), # Fetch all games from DB
        widget=forms.CheckboxSelectMultiple, # Render as checkboxes
        required=True,
        help_text="Select all games included in this tournament."
    )

    class Meta:
        model = Tournament
        fields = ['name', 'start_date', 'games']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Summer Cricket Cup'}),
        }
        labels = {
            'name': 'Tournament Name',
            'start_date': 'Tournament Start Date',
        }

