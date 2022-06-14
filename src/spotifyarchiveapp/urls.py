from django.urls import path
from . import views
from django.conf.urls import handler404

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('playlist/', views.playlist, name='playlist'),
    path('success/', views.success, name='success'),
]

handler404 = 'spotifyarchiveapp.views.error404'