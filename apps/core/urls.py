#apps/core/urls-py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    #path('', views.home_view, name='home'),
    path('sobre/', views.sobre_view, name='sobre'),
    path('contato/', views.contacto_view, name='contato'),
    path('sobre/termos', views.termos_view, name='termos'),
    path('sobre/politicas', views.politicas_view, name='politicas'),
    
    path('', views.HomeView.as_view(), name='home'),
    
]
