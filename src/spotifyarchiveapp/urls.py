from django.urls import path
from . import views
from django.conf.urls import handler404

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('success/', views.success, name='success'),
    path('error404/', views.handler404, name='error404'),
]

handler404 = 'spotifyarchiveapp.views.handler404'