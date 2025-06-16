from django.urls import path
from apps.home import views

app_name = 'home' # Defines the namespace for your app

urlpatterns = [
    path('', views.home_view, name='home'), # Your homepage view
]