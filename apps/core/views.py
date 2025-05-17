# apps/core/views.py
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.db.models import Q
from apps.produtos.models import Categoria, Produto, ImagemProduto, Marca


def home_view(request):
    return render(request, 'core/home.html')

def sobre_view(request):
    return render(request, 'core/sobre.html')

def contacto_view(request):
    return render(request, 'core/contato.html')

def termos_view(request):
    return render(request, 'core/termos_de_uso.html')

def politicas_view(request):
    return render(request, 'core/politicas_privacidade.html')

class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter categorias em destaque (limitada a 3)
        context['categorias_destaque'] = Categoria.objects.filter(
            status=True
        ).order_by('?')[:3]  # ordem aleatória, 3 primeiras
        
        # Obter produtos em destaque
        context['produtos_destaque'] = Produto.objects.filter(
            destaque=True, 
            status=True
        ).order_by('-data_cadastro')[:4]
        
        # Para cada produto, obter sua primeira imagem (ou None)
        for produto in context['produtos_destaque']:
            imagem = ImagemProduto.objects.filter(produto=produto).order_by('ordem').first()
            produto.imagem_principal = imagem.url_imagem if imagem else None
        
        # Obter marcas parceiras (limitada a 6)
        context['marcas'] = Marca.objects.filter(
            status=True
        ).order_by('?')[:6]  # ordem aleatória, 6 primeiras
        
        return context