# apps/produtos/views.py
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from apps.produtos.models import Produto, Marca, Categoria, Avaliacao, Visita

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse


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
        
        # Adicionando avaliações do produto ao contexto
        context['avaliacoes'] = self.object.avaliacoes.filter(status=True)
        
        # Verificar se o usuário já avaliou o produto
        if self.request.user.is_authenticated:
            context['avaliacao_usuario'] = Avaliacao.objects.filter(
                produto=self.object,
                usuario=self.request.user
            ).first()
        
        return context
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        # Registrar visita
        produto = self.object
        
        # Dados para registro da visita
        ip = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        usuario = request.user if request.user.is_authenticated else None
        
        # Criar registro de visita
        Visita.objects.create(
            produto=produto,
            usuario=usuario,
            ip=ip,
            user_agent=user_agent
        )
        
        return response

@login_required
def avaliar_produto(request, produto_id):
    if request.method == 'POST':
        produto = get_object_or_404(Produto, id=produto_id, status=True)
        nota = request.POST.get('nota')
        comentario = request.POST.get('comentario', '')
        
        # Validação da nota
        try:
            nota = int(nota)
            if nota < 1 or nota > 5:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Nota inválida. Deve ser entre 1 e 5.'
                    })
                messages.error(request, 'Nota inválida. Deve ser entre 1 e 5.')
                return redirect('produtos:detalhe', pk=produto_id)
        except (ValueError, TypeError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Nota inválida.'
                })
            messages.error(request, 'Nota inválida.')
            return redirect('produtos:detalhe', pk=produto_id)
        
        # Verificar se o usuário já avaliou este produto
        avaliacao_existente = Avaliacao.objects.filter(
            produto=produto,
            usuario=request.user
        ).first()
        
        if avaliacao_existente:
            # Atualizar avaliação existente
            avaliacao_existente.nota = nota
            avaliacao_existente.comentario = comentario
            avaliacao_existente.save()
            mensagem = 'Sua avaliação foi atualizada com sucesso!'
        else:
            # Criar nova avaliação
            Avaliacao.objects.create(
                produto=produto,
                usuario=request.user,
                nota=nota,
                comentario=comentario
            )
            mensagem = 'Sua avaliação foi enviada com sucesso!'
        
        # Responder adequadamente para AJAX ou requisições normais
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': mensagem
            })
        
        messages.success(request, mensagem)
        return redirect('produtos:detalhe', pk=produto_id)
    
    # Se não for POST, redirecionar para a página do produto
    return redirect('produtos:detalhe', pk=produto_id)

@login_required
def remover_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, usuario=request.user)
    produto_id = avaliacao.produto.id
    
    avaliacao.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Avaliação removida com sucesso!'
        })
    
    messages.success(request, 'Avaliação removida com sucesso!')
    return redirect('produtos:detalhe', pk=produto_id)