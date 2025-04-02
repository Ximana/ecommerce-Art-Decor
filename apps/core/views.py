# apps/core/views.py
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

def home_view(request):
    return render(request, 'core/home.html')

def sobre_view(request):
    return render(request, 'core/sobre.html')