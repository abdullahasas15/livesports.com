from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('live/', views.live_view, name='live'),
    path('admin/', views.admin_panel, name='admin'),
]
