from django.urls import path
from . import views
app_name = 'tournaments'
urlpatterns = [
    path('', views.tournaments_view, name='tournaments'),
]