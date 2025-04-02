# apps/pedidos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse

from apps.carrinhos.models import Carrinho
from apps.usuarios.models import Endereco
from apps.pagamentos.models import MetodoPagamento
from .models import Pedido, ItemPedido, FormaEnvio, HistoricoPedido
from .forms import EnderecoEntregaForm

class CheckoutView(LoginRequiredMixin, View):
    """
    View para exibir a página de checkout e processar as informações para finalização do pedido
    """
    login_url = '/usuarios/login/'
    template_name = 'pedidos/checkout.html'
    
    def get(self, request, *args, **kwargs):
        # Obter o carrinho do usuário
        carrinho, created = Carrinho.objects.get_or_create(usuario=request.user)
        
        # Verificar se há itens no carrinho
        if carrinho.itens.count() == 0:
            messages.warning(request, 'Seu carrinho está vazio. Adicione produtos antes de finalizar a compra.')
            return redirect('carrinhos:listar')
            
        # Verificar estoque dos itens
        for item in carrinho.itens.all():
            estoque_disponivel = item.produto.estoque
            if item.variacao:
                estoque_disponivel = item.variacao.estoque
                
            if item.quantidade > estoque_disponivel:
                messages.error(
                    request, 
                    f'Quantidade indisponível para o produto {item.produto.nome}. '
                    f'Estoque atual: {estoque_disponivel}'
                )
                return redirect('carrinhos:listar')
        
        # Obter endereços do usuário
        enderecos = request.user.enderecos.all()
        
        # Se não houver endereços cadastrados, redirecionar para cadastro de endereço
        if not enderecos.exists():
            messages.info(request, 'Por favor, cadastre um endereço antes de finalizar a compra.')
            # Assumindo que você tem uma URL para adicionar endereço
            return redirect('usuarios:listar_enderecos')
        
        # Obter formas de envio ativas
        formas_envio = FormaEnvio.objects.filter(status=True)
        
        # Obter métodos de pagamento ativos
        metodos_pagamento = MetodoPagamento.objects.filter(status=True)
        
        # Calcular totais
        subtotal = carrinho.calcular_total()
        
        # Inicialmente sem frete (será calculado via AJAX quando o usuário selecionar a forma de envio)
        frete = 0
        total = subtotal + frete
        
        context = {
            'carrinho': carrinho,
            'itens': carrinho.itens.all(),
            'enderecos': enderecos,
            'formas_envio': formas_envio,
            'metodos_pagamento': metodos_pagamento,
            'subtotal': subtotal,
            'frete': frete,
            'total': total,
            'quantidade_itens': carrinho.quantidade_total_itens()
        }
        
        return render(request, self.template_name, context)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Obter o carrinho do usuário
        carrinho = get_object_or_404(Carrinho, usuario=request.user)
        
        # Verificar se há itens no carrinho
        if carrinho.itens.count() == 0:
            messages.warning(request, 'Seu carrinho está vazio. Adicione produtos antes de finalizar a compra.')
            return redirect('carrinhos:listar')
        
        # Obter dados do formulário
        endereco_entrega_id = request.POST.get('endereco_entrega')
        endereco_cobranca_id = request.POST.get('endereco_cobranca', endereco_entrega_id)  # Usa o mesmo de entrega se não for especificado
        forma_envio_id = request.POST.get('forma_envio')
        metodo_pagamento_id = request.POST.get('metodo_pagamento')
        observacoes = request.POST.get('observacoes', '')
        
        # Validar dados recebidos
        if not all([endereco_entrega_id, forma_envio_id, metodo_pagamento_id]):
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return redirect('pedidos:checkout')
        
        try:
            # Obter objetos relacionados
            endereco_entrega = Endereco.objects.get(id=endereco_entrega_id, usuario=request.user)
            endereco_cobranca = Endereco.objects.get(id=endereco_cobranca_id, usuario=request.user) if endereco_cobranca_id != endereco_entrega_id else endereco_entrega
            forma_envio = FormaEnvio.objects.get(id=forma_envio_id, status=True)
            metodo_pagamento = MetodoPagamento.objects.get(id=metodo_pagamento_id, status=True)
            
            # Calcular valores
            subtotal = carrinho.calcular_total()
            valor_frete = forma_envio.taxa_fixa or 0
            # Aqui você poderia implementar lógicas de desconto, cupons, etc.
            valor_desconto = 0
            valor_total = subtotal + valor_frete - valor_desconto
            
            # Criar o pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                endereco_entrega=endereco_entrega,
                endereco_cobranca=endereco_cobranca,
                forma_envio=forma_envio,
                metodo_pagamento=metodo_pagamento,
                subtotal=subtotal,
                valor_frete=valor_frete,
                valor_desconto=valor_desconto,
                valor_total=valor_total,
                observacoes=observacoes
            )
            
            # Registrar histórico inicial
            pedido.registrar_status('aguardando_pagamento', 'Pedido criado')
            
            # Criar itens do pedido baseados no carrinho
            for item_carrinho in carrinho.itens.all():
                # Calcular preço unitário considerando variação
                preco_unitario = item_carrinho.produto.preco_venda
                if item_carrinho.variacao:
                    preco_unitario += item_carrinho.variacao.valor
                
                # Criar item do pedido
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=item_carrinho.produto,
                    variacao=item_carrinho.variacao,
                    quantidade=item_carrinho.quantidade,
                    preco_unitario=preco_unitario,
                    preco_total=preco_unitario * item_carrinho.quantidade
                )
                
                # Atualizar estoque
                if item_carrinho.variacao:
                    item_carrinho.variacao.estoque -= item_carrinho.quantidade
                    item_carrinho.variacao.save()
                else:
                    item_carrinho.produto.estoque -= item_carrinho.quantidade
                    item_carrinho.produto.save()
            
            # Limpar o carrinho após finalizar o pedido
            carrinho.itens.all().delete()
            
            messages.success(request, f'Seu pedido {pedido.codigo_pedido} foi realizado com sucesso!')
            return redirect('pedidos:confirmacao', codigo=pedido.codigo_pedido)
            
        except (Endereco.DoesNotExist, FormaEnvio.DoesNotExist, MetodoPagamento.DoesNotExist) as e:
            messages.error(request, f'Erro ao processar o pedido: {str(e)}')
            return redirect('pedidos:checkout')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro inesperado: {str(e)}')
            return redirect('pedidos:checkout')


class ConfirmacaoPedidoView(LoginRequiredMixin, View):
    """
    View para exibir a página de confirmação após a finalização do pedido
    """
    login_url = '/usuarios/login/'
    template_name = 'pedidos/confirmacao.html'
    
    def get(self, request, codigo, *args, **kwargs):
        pedido = get_object_or_404(Pedido, codigo_pedido=codigo, usuario=request.user)
        
        context = {
            'pedido': pedido,
            'itens': pedido.itens.all()
        }
        
        return render(request, self.template_name, context)


class MeusPedidosView(LoginRequiredMixin, View):
    """
    View para listar todos os pedidos do usuário logado
    """
    login_url = '/usuarios/login/'
    template_name = 'pedidos/meus_pedidos.html'
    
    def get(self, request, *args, **kwargs):
        pedidos = Pedido.objects.filter(usuario=request.user).order_by('-data_pedido')
        
        context = {
            'pedidos': pedidos
        }
        
        return render(request, self.template_name, context)


class DetalhePedidoView(LoginRequiredMixin, View):
    """
    View para exibir os detalhes de um pedido específico
    """
    login_url = '/usuarios/login/'
    template_name = 'pedidos/detalhe_pedido.html'
    
    def get(self, request, codigo, *args, **kwargs):
        pedido = get_object_or_404(Pedido, codigo_pedido=codigo, usuario=request.user)
        
        context = {
            'pedido': pedido,
            'itens': pedido.itens.all(),
            'historico': pedido.historico.all()
        }
        
        return render(request, self.template_name, context)


class CancelarPedidoView(LoginRequiredMixin, View):
    """
    View para cancelar um pedido
    """
    login_url = '/usuarios/login/'
    
    def post(self, request, codigo, *args, **kwargs):
        pedido = get_object_or_404(Pedido, codigo_pedido=codigo, usuario=request.user)
        
        # Verificar se o pedido pode ser cancelado (apenas em determinados status)
        status_permitidos = ['aguardando_pagamento', 'pagamento_aprovado', 'em_separacao']
        if pedido.status not in status_permitidos:
            messages.error(request, 'Este pedido não pode ser cancelado no status atual.')
            return redirect('pedidos:detalhe', codigo=pedido.codigo_pedido)
        
        try:
            with transaction.atomic():
                # Restaurar estoque dos produtos
                for item in pedido.itens.all():
                    try:
                        if item.variacao and hasattr(item.variacao, 'estoque'):
                            item.variacao.estoque += item.quantidade
                            item.variacao.save()
                        elif hasattr(item.produto, 'estoque'):
                            item.produto.estoque += item.quantidade
                            item.produto.save()
                    except Exception as e:
                        # Log o erro, mas continue com o cancelamento
                        logger.error(f"Erro ao restaurar estoque: {str(e)}")
                
                # Registrar cancelamento no histórico
                pedido.registrar_status('cancelado', 'Pedido cancelado pelo cliente')
                
                messages.success(request, 'Seu pedido foi cancelado com sucesso.')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao cancelar o pedido: {str(e)}')
        
        return redirect('pedidos:detalhe', codigo=pedido.codigo_pedido)
    
    

class ConfirmarEntregaPedidoView(LoginRequiredMixin, View):
    """
    View para confirmar o recebimento de um pedido
    """
    login_url = '/usuarios/login/'
    
    def post(self, request, codigo, *args, **kwargs):
        pedido = get_object_or_404(Pedido, codigo_pedido=codigo, usuario=request.user)
        
        # Verificar se o pedido está no status de enviado
        if pedido.status != 'em_transporte':
            messages.error(request, 'Este pedido não está disponível para confirmação de recebimento.')
            return redirect('pedidos:detalhe', codigo=pedido.codigo_pedido)
        
        # Atualizar status do pedido
        pedido.status = 'entregue'
        pedido.save()
        
        # Registrar no histórico
        pedido.registrar_status('entregue', 'Entrega confirmada pelo cliente')
        
        messages.success(request, 'Recebimento do pedido confirmado com sucesso!')
        return redirect('pedidos:detalhe', codigo=pedido.codigo_pedido)
    
# Funções auxiliares para AJAX
from django.http import JsonResponse

def calcular_frete_ajax(request):
    """
    Função para calcular o frete via AJAX quando o usuário seleciona uma forma de envio
    """
    if request.method == 'POST' and request.is_ajax():
        forma_envio_id = request.POST.get('forma_envio_id')
        
        try:
            forma_envio = FormaEnvio.objects.get(id=forma_envio_id)
            
            # Você pode implementar uma lógica mais complexa para cálculo de frete aqui
            # Por exemplo, considerar o peso dos produtos, distância, etc.
            valor_frete = forma_envio.taxa_fixa or 0
            
            # Calcular novo total
            if request.user.is_authenticated:
                carrinho = Carrinho.objects.get(usuario=request.user)
                subtotal = carrinho.calcular_total()
                total = subtotal + valor_frete
            else:
                # Para usuários não autenticados
                total = valor_frete  # Você precisará implementar essa parte
            
            return JsonResponse({
                'valor_frete': float(valor_frete),
                'total': float(total),
                'prazo_entrega': forma_envio.prazo_entrega
            })
            
        except FormaEnvio.DoesNotExist:
            return JsonResponse({'erro': 'Forma de envio não encontrada'}, status=400)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)