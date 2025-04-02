# apps/usuarios/views.py

from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.contrib import messages
from .models import Usuario, Endereco, ListaDesejo
from apps.produtos.models import Produto
from .forms import UsuarioRegistroForm, EnderecoForm #, UsuarioEdicaoForm
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.http import JsonResponse
#import json

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #messages.success(request, 'Login realizado com sucesso!')
            return redirect('core:home')
        else:
            messages.error(request, 'Usuário ou senha inválidos')
    return render(request, 'usuarios/login.html')

@login_required
def logout_view(request):
    logout(request)
    #messages.success(request, 'Logout realizado com sucesso!')
    return redirect('core:home')


def home_view(request):
    return render(request, 'core/home.html')

def listaDesejos_view(request):
    return render(request, 'usuarios/lista_desejos.html')

class ListaDesejoView(LoginRequiredMixin, ListView):
    model = ListaDesejo
    template_name = 'usuarios/lista_desejos.html'
    context_object_name = 'itens'
    
    def get_queryset(self):
        return ListaDesejo.objects.filter(usuario=self.request.user)

class AdicionarListaDesejoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        produto_id = request.POST.get('produto_id')
        produto = get_object_or_404(Produto, id=produto_id, status=True)
        
        # Verificar se já existe na lista de desejos
        desejo, created = ListaDesejo.objects.get_or_create(
            usuario=request.user,
            produto=produto
        )
        
        # Resposta para AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if created:
                return JsonResponse({
                    'status': 'success',
                    'message': f"{produto.nome} adicionado à sua lista de desejos.",
                    'added': True,
                    'count': ListaDesejo.objects.filter(usuario=request.user).count()
                })
            else:
                # Se já existe, remover da lista
                desejo.delete()
                return JsonResponse({
                    'status': 'success',
                    'message': f"{produto.nome} removido da sua lista de desejos.",
                    'added': False,
                    'count': ListaDesejo.objects.filter(usuario=request.user).count()
                })
        
        # Resposta não-AJAX
        if created:
            messages.success(request, f"{produto.nome} adicionado à sua lista de desejos.")
        else:
            messages.info(request, f"{produto.nome} já está na sua lista de desejos.")
            
        return redirect('produtos:detalhe', pk=produto_id)

class RemoverListaDesejoView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        item = get_object_or_404(ListaDesejo, pk=pk, usuario=request.user)
        nome_produto = item.produto.nome
        item.delete()
        
        # Resposta para AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f"{nome_produto} removido da sua lista de desejos.",
                'count': ListaDesejo.objects.filter(usuario=request.user).count()
            })
        
        # Resposta não-AJAX
        messages.success(request, f"{nome_produto} removido da sua lista de desejos.")
        return redirect('usuarios:lista_desejos')
    
class EnderecoListView(LoginRequiredMixin, ListView):
    model = Endereco
    template_name = 'usuarios/enderecos/listar_enderecos.html'
    context_object_name = 'enderecos'
    
    def get_queryset(self):
        return Endereco.objects.filter(usuario=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = EnderecoForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = EnderecoForm(request.POST)
        if form.is_valid():
            endereco = form.save(commit=False)
            endereco.usuario = request.user
            
            # Se esse for o primeiro endereço ou marcado como principal
            if not Endereco.objects.filter(usuario=request.user).exists() or form.cleaned_data.get('principal'):
                # Desmarca outros endereços principais
                Endereco.objects.filter(usuario=request.user, principal=True).update(principal=False)
                endereco.principal = True
                
            endereco.save()
            messages.success(request, 'Endereço adicionado com sucesso!')
            return redirect('usuarios:listar_enderecos')
        
        # Se o formulário não for válido, retorna à lista com os erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class EnderecoUpdateView(LoginRequiredMixin, UpdateView):
    model = Endereco
    form_class = EnderecoForm
    template_name = 'usuarios/enderecos/editar_endereco.html'
    
    def get_queryset(self):
        return Endereco.objects.filter(usuario=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('usuarios:listar_enderecos')
    
    def form_valid(self, form):
        # Se marcado como principal, desmarca outros endereços principais
        if form.cleaned_data.get('principal'):
            Endereco.objects.filter(usuario=self.request.user, principal=True).exclude(pk=self.object.pk).update(principal=False)
        
        messages.success(self.request, 'Endereço atualizado com sucesso!')
        return super().form_valid(form)

class EnderecoDeleteView(LoginRequiredMixin, DeleteView):
    model = Endereco
    template_name = 'usuarios/enderecos/confirmar_exclusao.html'
    success_url = reverse_lazy('usuarios:listar_enderecos')
    
    def get_queryset(self):
        return Endereco.objects.filter(usuario=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        
        # Verificar se era o endereço principal antes de excluir
        era_principal = self.object.principal
        
        self.object.delete()
        
        # Se era principal e existem outros endereços, tornar um deles o principal
        if era_principal:
            enderecos_restantes = Endereco.objects.filter(usuario=request.user)
            if enderecos_restantes.exists():
                endereco_novo_principal = enderecos_restantes.first()
                endereco_novo_principal.principal = True
                endereco_novo_principal.save()
        
        messages.success(request, 'Endereço removido com sucesso!')
        return redirect(success_url)

def definir_endereco_principal(request, pk):
    """Define um endereço como principal e desmarca os demais"""
    if request.method == 'POST':
        endereco = get_object_or_404(Endereco, pk=pk, usuario=request.user)
        
        # Desmarca todos os endereços principais do usuário
        Endereco.objects.filter(usuario=request.user, principal=True).update(principal=False)
        
        # Define o endereço selecionado como principal
        endereco.principal = True
        endereco.save()
        
        messages.success(request, 'Endereço principal atualizado com sucesso!')
        
        # Verifica se é uma requisição AJAX/XHR usando o cabeçalho HTTP_X_REQUESTED_WITH
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        return redirect('usuarios:listar_enderecos')
    
    return redirect('usuarios:listar_enderecos')