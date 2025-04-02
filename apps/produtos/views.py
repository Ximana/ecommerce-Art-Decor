# apps/produtos/views.py
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from apps.produtos.models import Produto, Marca, Categoria

"""
from django.shortcuts import render


def lista_view(request):
    return render(request, 'produtos/listar.html')

def detalhe_view(request):
    return render(request, 'produtos/detalhes.html')
"""

class ProdutoListView(ListView):
    model = Produto
    template_name = 'produtos/listar.html'
    context_object_name = 'produtos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Produto.objects.filter(status=True)
        
        # Filtro por categoria
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        # Filtro por marca
        marca_id = self.request.GET.get('marca')
        if marca_id:
            queryset = queryset.filter(marca_id=marca_id)
        
        # Filtro por preço
        preco_maximo = self.request.GET.get('preco_max')
        if preco_maximo:
            try:
                preco_maximo = float(preco_maximo)
                queryset = queryset.filter(preco_venda__lte=preco_maximo)
            except (ValueError, TypeError):
                pass
        
        # Ordenação
        ordem = self.request.GET.get('ordem')
        if ordem:
            if ordem == 'nome_asc':
                queryset = queryset.order_by('nome')
            elif ordem == 'nome_desc':
                queryset = queryset.order_by('-nome')
            elif ordem == 'preco_asc':
                queryset = queryset.order_by('preco_venda')
            elif ordem == 'preco_desc':
                queryset = queryset.order_by('-preco_venda')
            elif ordem == 'recentes':
                queryset = queryset.order_by('-data_cadastro')
        else:
            # Ordenação padrão
            queryset = queryset.order_by('-destaque', 'nome')
            
        # Pesquisa
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) | 
                Q(descricao__icontains=q) |
                Q(marca__nome__icontains=q)
            )
            
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pega as categorias e marcas ativas
        context['categorias'] = Categoria.objects.filter(status=True)
        context['marcas'] = Marca.objects.filter(status=True)
        
        # Adiciona os filtros atuais ao contexto para manter estado
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        context['marca_selecionada'] = self.request.GET.get('marca', '')
        context['ordem_selecionada'] = self.request.GET.get('ordem', '')
        context['preco_maximo'] = self.request.GET.get('preco_max', 500)
        context['pesquisa'] = self.request.GET.get('q', '')
        
        # Contagem de produtos
        context['total_produtos'] = self.get_queryset().count()
        
        return context

class ProdutoDetailView(DetailView):
    model = Produto
    template_name = 'produtos/detalhes.html'
    context_object_name = 'produto'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Produtos relacionados (mesma categoria)
        context['produtos_relacionados'] = Produto.objects.filter(
            categoria=self.object.categoria,
            status=True
        ).exclude(id=self.object.id)[:4]
        
        return context

