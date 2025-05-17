
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
from apps.produtos.models import Produto, Marca, Categoria, ImagemProduto
from .forms import ProdutoRegistroForm, MarcaRegistroForm, CategoriaRegistroForm, ProdutoImageForm, MovimentoEstoqueForm
from django.db.models import Q, Avg
from django.http import JsonResponse
import json

class ProdutoListView(ListView):
    model = Produto
    template_name = 'administracao/produtos/listaProdutos.html'
    context_object_name = 'produtos'
    paginate_by = 10
    
    # Função para pesquisa de produtos
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search query filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) |
                Q(codigo_barras__icontains=search_query)
            )
        
        # Categoria filter
        categoria_id = self.request.GET.get('categoria', '')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        # Marca filter
        marca_id = self.request.GET.get('marca', '')
        if marca_id:
            queryset = queryset.filter(marca_id=marca_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add context for filters
        context['categorias'] = Categoria.objects.filter(status=True)
        context['marcas'] = Marca.objects.filter(status=True)
        
        # Preserve filter and search parameters
        context['search_query'] = self.request.GET.get('search', '')
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        context['marca_selecionada'] = self.request.GET.get('marca', '')
        
        # Add form for product registration
        context['form'] = ProdutoRegistroForm()
        
        return context
    
    def post(self, request, *args, **kwargs):
        form = ProdutoRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            # Separa a imagem antes de salvar o produto
            primeira_imagem = form.cleaned_data.pop('primeira_imagem', None)
            
            produto = Produto.objects.create(**form.cleaned_data)
            
            # Se uma imagem foi enviada, cria o objeto ImagemProduto
            if primeira_imagem:
                ImagemProduto.objects.create(
                    produto=produto,
                    url_imagem=primeira_imagem
                )
            
            #messages.success(request, f'Produto {produto.nome} cadastrado com sucesso!')
            return redirect(produto.get_absolute_url())
 
        
        
        # Se o formulário não for válido, retorna à lista com os erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class ProdutoDetailView(LoginRequiredMixin, DetailView):
    model = Produto
    template_name = 'administracao/produtos/detalheProduto.html'
    context_object_name = 'produto'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProdutoRegistroForm(instance=self.object)
        context['image_form'] = ProdutoImageForm()
        context['estoque_form'] = MovimentoEstoqueForm()
        
        # Carrega o histórico de movimentações de estoque
        context['movimentos_estoque'] = self.object.movimentos_estoque.all()[:10]
        
        # Carrega as visitas ao produto
        context['visitas'] = self.object.visitas.all().order_by('-data_visita')[:20]
        
        # Carrega as avaliações do produto com média
        avaliacoes = self.object.avaliacoes.filter(status=True).order_by('-data_avaliacao')
        context['avaliacoes'] = avaliacoes
        context['avaliacoes_media'] = avaliacoes.aggregate(Avg('nota'))['nota__avg'] or 0
        
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Movimentacoes ee stock
        if 'adicionar_estoque' in request.POST:
            estoque_form = MovimentoEstoqueForm(request.POST)
            if estoque_form.is_valid():
                movimento = estoque_form.save(commit=False)
                movimento.produto = self.object
                movimento.save()
                messages.success(request, f'Estoque atualizado: {movimento.quantidade} {movimento.get_tipo_display()}')
                return redirect(self.object.get_absolute_url())
            else:
                messages.error(request, 'Erro ao adicionar movimento de estoque.')
                return self.get(request, *args, **kwargs)
        
        
        # upload de imagem
        if 'upload_image' in request.POST:
            image_form = ProdutoImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                image = image_form.save(commit=False)
                image.produto = self.object
                image.save()
                messages.success(request, 'Imagem adicionada com sucesso!')
                return redirect(self.object.get_absolute_url())
        
        # remover imagens
        if 'delete_image' in request.POST:
            image_id = request.POST.get('image_id')
            try:
                image = ImagemProduto.objects.get(id=image_id, produto=self.object)
                image.delete()
                messages.success(request, 'Imagem removida com sucesso!')
                return redirect(self.object.get_absolute_url())
            except ImagemProduto.DoesNotExist:
                messages.error(request, 'Imagem não encontrada.')
                return redirect(self.object.get_absolute_url())
        
        return super().get(request, *args, **kwargs)
    
class ProdutoDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Produto
    success_url = reverse_lazy('administracao:listaProdutos')
    success_message = "Produto removido com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
    
class ProdutoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Produto
    form_class = ProdutoRegistroForm
    template_name = 'administracao/produtos/detalheProduto.html'  # Apontamos para detalhe já que o modal está lá
    success_message = "Dados do produto %(nome)s foram atualizados com sucesso!"
    
    def get_success_url(self):
        return reverse_lazy('administracao:produto_detalhe', kwargs={'pk': self.object.pk})
    
    def form_invalid(self, form):
        # Em caso de erro, retorna para a página de detalhes com o formulário e erros
        return render(self.request, self.template_name, {
            'produto': self.get_object(),
            'form': form
        })


class MarcaListView(ListView):
    model = Marca
    template_name = 'administracao/produtos/marcas/listaMarca.html'
    context_object_name = 'marcas'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(nome__icontains=search_query)
        return queryset
    
    def post(self, request, *args, **kwargs):
        form = MarcaRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            marca = form.save()
            messages.success(request, 'Marca cadastrado com sucesso!')
            #return redirect(marca.get_absolute_url())
            return redirect('administracao:marca_lista')
        
        # Se o formulário não for válido, retorna à lista com os erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class MarcaUpdateView(UpdateView):
    model = Marca
    form_class = MarcaRegistroForm
    template_name = 'administracao/produtos/marcas/marca_editar.html'
    success_url = reverse_lazy('produtos:marca_lista')

    def form_valid(self, form):
        messages.success(self.request, f'Marca "{form.instance.nome}" atualizada com sucesso!')
        return super().form_valid(form)

class MarcaDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Marca
    success_url = reverse_lazy('administracao:marca_lista')
    success_message = "Marca removido com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
    

class CategoriaListView(ListView):
    model = Categoria
    template_name = 'administracao/produtos/categorias/listaCategoria.html'
    context_object_name = 'categorias'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '').strip()
        
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) |
                Q(descricao__icontains=search_query) |
                Q(categoria_pai__nome__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CategoriaRegistroForm()
        context['search_query'] = self.request.GET.get('search', '')
        context['categorias'] = Categoria.objects.all()  # To populate categoria pai dropdown
        return context
    
    def post(self, request, *args, **kwargs):
        form = CategoriaRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, 'Categoria cadastrada com sucesso!')
            return redirect('administracao:categoria_lista')
        
        # Se o formulário não for válido, retorna à lista com os erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class CategoriaUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaRegistroForm
    template_name = 'administracao/produtos/categorias/categoria_editar.html'
    success_url = reverse_lazy('produtos:categoria_lista')

    def form_valid(self, form):
        messages.success(self.request, f'Categoria "{form.instance.nome}" atualizada com sucesso!')
        return super().form_valid(form)

class CategoriaDeleteView(DeleteView):
    model = Categoria
    success_url = reverse_lazy('administracao:categoria_lista')
    success_message = "Categoria removido com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
    