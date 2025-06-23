# livesports_project/apps/viewer/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from apps.tournaments.models import UserProfile, Game # Import UserProfile and Game

class ViewerSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your First Name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Last Name'}))
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        help_text="Format: YYYY-MM-DD"
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about yourself...'}),
        required=False, # Make it optional for signup
        label="About Me"
    )
    fav_sports = forms.ModelMultipleChoiceField(
        queryset=Game.objects.all().order_by('name'), # Fetch all games
        widget=forms.CheckboxSelectMultiple,
        required=False, # Make it optional for signup
        help_text="Select your favorite sports."
    )


    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'date_of_birth', 'bio', 'fav_sports')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # The UserProfile is guaranteed to exist due to the signal
            user_profile = user.userprofile
            user_profile.first_name = self.cleaned_data['first_name']
            user_profile.last_name = self.cleaned_data['last_name']
            user_profile.date_of_birth = self.cleaned_data['date_of_birth']
            user_profile.bio = self.cleaned_data['bio'] # Save new bio field
            user_profile.save()
            
            # Handle ManyToMany field for fav_sports
            if 'fav_sports' in self.cleaned_data:
                user_profile.fav_sports.set(self.cleaned_data['fav_sports']) # Set selected sports
        return user

