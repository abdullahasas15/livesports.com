from django.shortcuts import render

def tournaments_view(request):
    return render(request, 'tournaments/tournaments.html')