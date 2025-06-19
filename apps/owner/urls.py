from django.urls import path
from . import views
app_name = 'owner'
urlpatterns = [
    path('', views.index, name='index'),
]