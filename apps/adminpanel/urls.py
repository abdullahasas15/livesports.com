# adminpanel/urls.py
from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('login/', views.admin_login_signup, name='login_signup'),
    path('logout/', views.admin_logout_view, name='logout'), # Add logout URL
    path('create-tournament/', views.create_tournament_view, name='create_tournament'),
    path('dashboard/', views.admin_dashboard_view, name='dashboard'),
]
