from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('success/', views.success, name='success'),
    path('stats/', views.stats, name='stats'),
]