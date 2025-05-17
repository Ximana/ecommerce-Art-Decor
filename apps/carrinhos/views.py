# apps/carrinhos/views.py
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import Carrinho, ItemCarrinho
from apps.produtos.models import Produto, VariacaoProduto
from django.contrib import messages
from django.http import JsonResponse
import json

class CarrinhoListView(View):
    template_name = 'carrinhos/listar.html'
    
    def get(self, request, *args, **kwargs):
        # Para usuários logados, busca o carrinho associado ao usuário
        if request.user.is_authenticated:
            carrinho, created = Carrinho.objects.get_or_create(usuario=request.user, defaults={})
        # Para usuários não logados, verifica se há um token no cookie
        else:
            token = request.COOKIES.get('carrinho_token')
            if token:
                carrinho, created = Carrinho.objects.get_or_create(token=token, defaults={'token': token})
            else:
                # Cria um novo carrinho com token
                carrinho = Carrinho.objects.create()
                response = render(request, self.template_name, {'carrinho': carrinho})
                response.set_cookie('carrinho_token', carrinho.token, max_age=60*60*24*30)  # 30 dias
                return response
        
        # Calcula os valores totais
        subtotal = carrinho.calcular_total()
        
        context = {
            'carrinho': carrinho,
            'itens': carrinho.itens.all(),
            'subtotal': subtotal,
            'total': subtotal,  # Aqui você pode adicionar frete ou descontos se necessário
            'quantidade_itens': carrinho.quantidade_total_itens()
        }
        
        return render(request, self.template_name, context)
    

class AtualizarItemCarrinhoView(View):
    def post(self, request, pk, *args, **kwargs):
        item = get_object_or_404(ItemCarrinho, pk=pk)
        
        # Verificar se o item pertence ao carrinho do usuário atual
        if request.user.is_authenticated:
            if item.carrinho.usuario != request.user:
                return redirect('carrinhos:lista')
        else:
            token = request.COOKIES.get('carrinho_token')
            if not token or item.carrinho.token != token:
                return redirect('carrinhos:lista')
        
        try:
            quantidade = int(request.POST.get('quantidade', 1))
            if quantidade > 0:
                # Verificar estoque disponível
                estoque_disponivel = item.variacao.estoque if item.variacao else item.produto.estoque
                if quantidade <= estoque_disponivel:
                    item.quantidade = quantidade
                    item.save()
                else:
                    # Mensagem de erro (pode usar django messages framework)
                    pass
        except ValueError:
            pass  # Tratamento de erro se quantidade não for um número válido
        
        return redirect('carrinhos:lista')

class RemoverItemCarrinhoView(View):
    def post(self, request, pk, *args, **kwargs):
        item = get_object_or_404(ItemCarrinho, pk=pk)
        
        # Verificar se o item pertence ao carrinho do usuário atual
        if request.user.is_authenticated:
            if item.carrinho.usuario != request.user:
                return redirect('carrinhos:lista')
        else:
            token = request.COOKIES.get('carrinho_token')
            if not token or item.carrinho.token != token:
                return redirect('carrinhos:lista')
        
        item.delete()
        return redirect('carrinhos:lista')
    
class AdicionarAoCarrinhoView(View):
    def post(self, request, *args, **kwargs):
        # Obter dados do formulário
        produto_id = request.POST.get('produto_id')
        variacao_id = request.POST.get('variacao_id')
        quantidade = int(request.POST.get('quantidade', 1))
        
        # Validar produto
        produto = get_object_or_404(Produto, id=produto_id, status=True)
        
        # Validar variação, se fornecida
        variacao = None
        if variacao_id:
            variacao = get_object_or_404(VariacaoProduto, id=variacao_id, produto=produto, status=True)
        
        # Verificar estoque
        estoque_disponivel = variacao.estoque if variacao else produto.estoque
        if quantidade > estoque_disponivel:
            #messages.error(request, f"Quantidade indisponível. Estoque atual: {estoque_disponivel}")
            return redirect('produtos:detalhe', pk=produto_id)
            
        # Obter ou criar o carrinho
        if request.user.is_authenticated:
            carrinho, created = Carrinho.objects.get_or_create(
                usuario=request.user,
                defaults={}
            )
        else:
            token = request.COOKIES.get('carrinho_token')
            if token:
                carrinho, created = Carrinho.objects.get_or_create(
                    token=token,
                    defaults={'token': token}
                )
            else:
                carrinho = Carrinho.objects.create()
        
        # Verificar se o item já existe no carrinho
        try:
            item_carrinho = ItemCarrinho.objects.get(
                carrinho=carrinho,
                produto=produto,
                variacao=variacao
            )
            # Atualizar quantidade se o item já existir
            nova_quantidade = item_carrinho.quantidade + quantidade
            if nova_quantidade <= estoque_disponivel:
                item_carrinho.quantidade = nova_quantidade
                item_carrinho.save()
                #messages.success(request, f"Quantidade de {produto.nome} atualizada no carrinho.")
            else:
                #messages.warning(request, f"Quantidade total excede o estoque disponível. Adicionado o máximo possível.")
                item_carrinho.quantidade = estoque_disponivel
                item_carrinho.save()
        except ItemCarrinho.DoesNotExist:
            # Criar novo item se não existir
            item_carrinho = ItemCarrinho(
                carrinho=carrinho,
                produto=produto,
                variacao=variacao,
                quantidade=quantidade
            )
            item_carrinho.save()
            #messages.success(request, f"{produto.nome} adicionado ao carrinho.")
        
        # Se for uma requisição AJAX, retornar JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f"{produto.nome} adicionado ao carrinho.",
                'quantidade_total': carrinho.quantidade_total_itens()
            })
        
        # Se for uma requisição normal, redirecionar para o carrinho
        response = redirect('carrinhos:lista')
        
        # Se for um usuário não logado e carrinho recém-criado, definir cookie
        if not request.user.is_authenticated and created:
            response.set_cookie('carrinho_token', carrinho.token, max_age=60*60*24*30)  # 30 dias
            
        return response