#/apps/administracao/views.py
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from apps.usuarios.models import Usuario
from apps.usuarios.forms import UsuarioRegistroForm #, UsuarioEdicaoForm
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.http import JsonResponse
import json

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #messages.success(request, 'Login realizado com sucesso!')
            return redirect('administracao:home')
        else:
            messages.error(request, 'Usuário ou senha inválidos')
    return render(request, 'administracao/login.html')

@login_required
def logout_view(request):
    logout(request)
    #messages.success(request, 'Logout realizado com sucesso!')
    return redirect('administracao:login')

@login_required
def home_view(request):
    return render(request, 'administracao/dashboard/home.html')

