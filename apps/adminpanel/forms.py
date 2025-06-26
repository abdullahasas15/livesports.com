# livesports_project/apps/adminpanel/forms.py
from django import forms
from apps.tournaments.models import Tournament, Game
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class AdminSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True      # This makes them a staff member (can access admin site if allowed)
        user.is_superuser = False # Explicitly set to False to differentiate from superuser
        if commit:
            user.save()
        return user

class AdminLoginForm(AuthenticationForm):
    pass

class TournamentCreationForm(forms.ModelForm):
    games = forms.ModelMultipleChoiceField(
        queryset=Game.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select all games included in this tournament."
    )

    num_teams = forms.IntegerField(
        label='Number of Teams',
        min_value=2,
        max_value=64,
        initial=4,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 8'})
    )

    class Meta:
        model = Tournament
        fields = ['name', 'start_date', 'games', 'num_teams']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Summer Cricket Cup'}),
        }
        labels = {
            'name': 'Tournament Name',
            'start_date': 'Tournament Start Date',
        }

