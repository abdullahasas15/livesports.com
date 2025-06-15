from django.urls import path
from . import views

urlpatterns = [
    path('', views.tournaments_view, name='tournaments'),
]