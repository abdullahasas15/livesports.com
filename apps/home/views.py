from django.shortcuts import render

def index(request):
    """
    Main homepage view - pure frontend interface
    """
    # This is just the interface - you can connect your models later
    context = {
        'live_count': 2,
        'upcoming_count': 5, 
        'finished_count': 12,
    }
    
    return render(request, 'home/index.html', context)

def live_view(request):
    """
    Live tournaments view
    """
    return render(request, 'tournaments/live.html')

def admin_panel(request):
    """
    Admin score update panel
    """
    return render(request, 'admin/score_update.html')
