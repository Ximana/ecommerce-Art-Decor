from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from apps.pedidos.models import FormaEnvio, Pedido, HistoricoPedido
from apps.pagamentos.models import Pagamento
from .forms import FormaEnvioForm
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.views import View
from django.http import JsonResponse

class FormaEnvioListView(LoginRequiredMixin, ListView):
    model = FormaEnvio
    template_name = 'administracao/pedidos/formaEnvio/listaFormaEnvio.html'
    context_object_name = 'formas_envio'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(nome__icontains=search_query)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FormaEnvioForm()
        context['form_editar'] = FormaEnvioForm()
        context['search_query'] = self.request.GET.get('search', '')
        return context
    
    def post(self, request, *args, **kwargs):
        form = FormaEnvioForm(request.POST)
        if form.is_valid():
            forma_envio = form.save()
            messages.success(request, 'Forma de envio cadastrada com sucesso!')
            return redirect('administracao:forma_envio_lista')
        
        # Se o formulário não for válido, retorna à lista com os erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class FormaEnvioUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = FormaEnvio
    form_class = FormaEnvioForm
    template_name = 'administracao/pedidos/listaFormaEnvio.html'
    success_url = reverse_lazy('administracao:forma_envio_lista')
    success_message = "Forma de envio atualizada com sucesso!"
    
    def form_valid(self, form):
        messages.success(self.request, f'Forma de envio "{form.instance.get_nome_display()}" atualizada com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao atualizar forma de envio. Verifique os dados informados.')
        return redirect('administracao:forma_envio_lista')

class FormaEnvioDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = FormaEnvio
    success_url = reverse_lazy('administracao:forma_envio_lista')
    success_message = "Forma de envio removida com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
    
class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'administracao/pedidos/listaPedidos.html'
    context_object_name = 'pedidos'
    paginate_by = 10
    login_url = '/usuarios/login/'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por busca
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(codigo_pedido__icontains=search_query) |
                Q(usuario__nome__icontains=search_query) |
                Q(usuario__email__icontains=search_query)
            )
        
        # Filtro por status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtro por método de pagamento
        metodo_pagamento = self.request.GET.get('metodo_pagamento', '')
        if metodo_pagamento:
            queryset = queryset.filter(metodo_pagamento_id=metodo_pagamento)
            
        # Filtro por data
        periodo = self.request.GET.get('periodo', '')
        hoje = timezone.now().date()
        
        if periodo == 'hoje':
            queryset = queryset.filter(data_pedido__date=hoje)
        elif periodo == 'ontem':
            ontem = hoje - timedelta(days=1)
            queryset = queryset.filter(data_pedido__date=ontem)
        elif periodo == 'semana':
            inicio_semana = hoje - timedelta(days=7)
            queryset = queryset.filter(data_pedido__date__gte=inicio_semana)
        elif periodo == 'mes':
            inicio_mes = hoje - timedelta(days=30)
            queryset = queryset.filter(data_pedido__date__gte=inicio_mes)
        elif periodo == 'personalizado':
            data_inicio = self.request.GET.get('data_inicio', '')
            data_fim = self.request.GET.get('data_fim', '')
            
            if data_inicio:
                queryset = queryset.filter(data_pedido__date__gte=data_inicio)
            if data_fim:
                queryset = queryset.filter(data_pedido__date__lte=data_fim)
        
        # Ordenação
        ordenacao = self.request.GET.get('ordenacao', '-data_pedido')
        return queryset.order_by(ordenacao)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar dados para os filtros
        from apps.pagamentos.models import MetodoPagamento
        
        context['status_opcoes'] = dict(Pedido.STATUS_CHOICES)
        context['metodos_pagamento'] = MetodoPagamento.objects.filter(status=True)
        
        # Preservar parâmetros de filtro e busca
        context['search_query'] = self.request.GET.get('search', '')
        context['status_selecionado'] = self.request.GET.get('status', '')
        context['metodo_pagamento_selecionado'] = self.request.GET.get('metodo_pagamento', '')
        context['periodo_selecionado'] = self.request.GET.get('periodo', '')
        context['data_inicio'] = self.request.GET.get('data_inicio', '')
        context['data_fim'] = self.request.GET.get('data_fim', '')
        context['ordenacao'] = self.request.GET.get('ordenacao', '-data_pedido')
        
        # Adicionar estatísticas rápidas
        context['total_pedidos'] = Pedido.objects.count()
        context['pedidos_aguardando_pagamento'] = Pedido.objects.filter(status='aguardando_pagamento').count()
        context['pedidos_em_andamento'] = Pedido.objects.filter(
            status__in=['pagamento_aprovado', 'em_separacao', 'em_transporte']
        ).count()
        context['pedidos_entregues'] = Pedido.objects.filter(status='entregue').count()
        context['pedidos_cancelados'] = Pedido.objects.filter(status='cancelado').count()
        
        return context
    
# da lista de pedidos
class AlterarStatusPedidoView(LoginRequiredMixin, View):
    login_url = '/usuarios/login/'
    
    def post(self, request):
        codigo_pedido = request.POST.get('codigo_pedido')
        novo_status = request.POST.get('novo_status')
        comentario = request.POST.get('comentario', '')
        
        # Buscar o pedido pelo código
        pedido = get_object_or_404(Pedido, codigo_pedido=codigo_pedido)
        status_anterior = pedido.status
        
        # Verificar transições válidas de status
        transicoes_invalidas = {
            'entregue': ['aguardando_pagamento'],
            'cancelado': ['entregue']
        }
        
        # Verificar se a transição é válida
        if novo_status in transicoes_invalidas.get(status_anterior, []):
            messages.error(
                request, 
                f"Transição de status inválida: de {pedido.get_status_display()} para {dict(Pedido.STATUS_CHOICES).get(novo_status)}"
            )
            return redirect('administracao:lista_pedidos')
        
        # Atualizar o status do pedido
        try:
            # Registrar no histórico e atualizar o status
            pedido.registrar_status(novo_status, comentario)
            
            # Sincronizar status de pagamento quando necessário
            self._sincronizar_status_pagamento(pedido, novo_status, request.user)
            
            messages.success(
                request, 
                f"Status do pedido {codigo_pedido} alterado com sucesso para {dict(Pedido.STATUS_CHOICES).get(novo_status)}"
            )
        except Exception as e:
            messages.error(request, f"Erro ao alterar status do pedido: {str(e)}")
        
        return redirect(reverse('administracao:lista_pedidos'))
    
    def _sincronizar_status_pagamento(self, pedido, novo_status, usuario):
        """
        Sincroniza o status do pagamento com o status do pedido quando necessário
        """
        # Se o pedido for marcado como pagamento aprovado ou em estados posteriores,
        # todos os pagamentos pendentes devem ser marcados como aprovados
        if novo_status in ['pagamento_aprovado', 'em_separacao', 'em_transporte', 'entregue']:
            pagamentos_pendentes = Pagamento.objects.filter(
                pedido=pedido, 
                status='pendente'
            )
            
            for pagamento in pagamentos_pendentes:
                pagamento.confirmar_pagamento(usuario=usuario, fonte='admin')
        
        # Se o pedido for cancelado, os pagamentos pendentes devem ser recusados
        elif novo_status == 'cancelado':
            pagamentos_pendentes = Pagamento.objects.filter(
                pedido=pedido, 
                status='pendente'
            )
            
            for pagamento in pagamentos_pendentes:
                pagamento.status = 'recusado'
                pagamento.data_processamento = timezone.now()
                pagamento.fonte_confirmacao = 'admin'
                pagamento.confirmado_por = usuario
                pagamento.observacoes_internas = "Pagamento recusado devido ao cancelamento do pedido."
                pagamento.save()
                
# para o detalhe do pedido
class PedidoDetailView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'administracao/pedidos/detalhePedido.html'
    context_object_name = 'pedido'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionando status disponíveis para o pedido
        context['status_opcoes'] = Pedido.STATUS_CHOICES
        # Adicionando status disponíveis para o pagamento
        context['pagamento_status_opcoes'] = Pagamento.STATUS_CHOICES
        return context

def alterar_status_pedido(request, pk):
    """
    View para alterar o status de um pedido via AJAX
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        pedido = get_object_or_404(Pedido, pk=pk)
        novo_status = request.POST.get('status')
        comentario = request.POST.get('comentario', '')
        
        # Verificar se o status é válido
        status_validos = [status[0] for status in Pedido.STATUS_CHOICES]
        if novo_status not in status_validos:
            return JsonResponse({'status': 'erro', 'mensagem': 'Status inválido'}, status=400)
        
        # Verificar regras de negócio para mudança de status
        status_atual = pedido.status
        
        # Regras para impedir alterações inválidas de status
        if status_atual == 'cancelado' and novo_status != 'cancelado':
            return JsonResponse({
                'status': 'erro', 
                'mensagem': 'Não é possível alterar o status de um pedido cancelado'
            }, status=400)
            
        if status_atual == 'entregue' and novo_status not in ['entregue', 'cancelado']:
            return JsonResponse({
                'status': 'erro', 
                'mensagem': 'Um pedido entregue só pode ser cancelado'
            }, status=400)
        
        # Verificar retrocesso de estados
        ordem_status = ['aguardando_pagamento', 'pagamento_aprovado', 'em_separacao', 'em_transporte', 'entregue']
        if status_atual in ordem_status and novo_status in ordem_status:
            pos_atual = ordem_status.index(status_atual)
            pos_novo = ordem_status.index(novo_status)
            
            if pos_novo < pos_atual:
                return JsonResponse({
                    'status': 'erro',
                    'mensagem': 'Não é permitido retroceder o status do pedido'
                }, status=400)
        
        # Registrar o novo status
        try:
            historico = pedido.registrar_status(novo_status, comentario)
            
            # Se o pedido for cancelado, tratar os pagamentos
            if novo_status == 'cancelado' and status_atual != 'cancelado':
                # Você pode adicionar aqui lógica para estornar pagamentos se necessário
                pass
                
            # Se o pedido avançar para status após o pagamento aprovado, verificar se existe pagamento aprovado
            if status_atual == 'aguardando_pagamento' and novo_status in ['pagamento_aprovado', 'em_separacao', 'em_transporte', 'entregue']:
                pagamento_aprovado = pedido.pagamentos.filter(status='aprovado').exists()
                if not pagamento_aprovado:
                    # Adicionar aviso no histórico sobre ausência de pagamento aprovado
                    pedido.registrar_status(
                        novo_status,
                        "ATENÇÃO: Status avançado sem pagamento aprovado registrado no sistema."
                    )
            
            return JsonResponse({
                'status': 'sucesso',
                'mensagem': 'Status atualizado com sucesso',
                'novo_status': pedido.get_status_display(),
                'data_atualizacao': historico.data_alteracao.strftime('%d/%m/%Y %H:%M')
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'erro', 
                'mensagem': f'Erro ao atualizar status: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'erro', 'mensagem': 'Método não permitido'}, status=405)

def alterar_status_pagamento(request, pk):
    """
    View para alterar o status de um pagamento via AJAX
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        pagamento = get_object_or_404(Pagamento, pk=pk)
        novo_status = request.POST.get('status')
        observacao = request.POST.get('observacao', '')
        
        # Verificar se o status é válido
        status_validos = [status[0] for status in Pagamento.STATUS_CHOICES]
        if novo_status not in status_validos:
            return JsonResponse({'status': 'erro', 'mensagem': 'Status inválido'}, status=400)
        
        # Guardar o status antigo para verificação
        status_antigo = pagamento.status
        
        # Verificar regras para evitar retrocesso de estados
        if status_antigo == 'aprovado' and novo_status == 'pendente':
            return JsonResponse({
                'status': 'erro', 
                'mensagem': 'Não é possível retroceder um pagamento aprovado para pendente'
            }, status=400)
        
        if status_antigo == 'recusado' and novo_status in ['pendente', 'aprovado']:
            return JsonResponse({
                'status': 'erro', 
                'mensagem': 'Não é possível alterar o status de um pagamento recusado'
            }, status=400)
        
        # Atualizar o status do pagamento
        pagamento.status = novo_status
        pagamento.data_processamento = timezone.now()
        
        # Adicionar observação com marcação de data/hora
        if observacao:
            timestamp = timezone.now().strftime('%d/%m/%Y %H:%M')
            nova_observacao = f"[{timestamp}] {observacao}"
            
            if pagamento.observacoes_internas:
                pagamento.observacoes_internas += f"\n{nova_observacao}"
            else:
                pagamento.observacoes_internas = nova_observacao
        
        # Se for aprovado e estiver mudando de status, configurar a confirmação
        if novo_status == 'aprovado' and status_antigo != 'aprovado':
            try:
                pagamento.confirmar_pagamento(request.user, 'admin')
            except Exception as e:
                return JsonResponse({
                    'status': 'erro', 
                    'mensagem': f'Erro ao confirmar pagamento: {str(e)}'
                }, status=500)
            
            # Atualizar o status do pedido para "pagamento_aprovado" se ainda estiver aguardando
            if pagamento.pedido.status == 'aguardando_pagamento':
                pagamento.pedido.status = 'pagamento_aprovado'
                pagamento.pedido.save()
                
                # Registrar histórico do pedido
                pagamento.pedido.registrar_status(
                    'pagamento_aprovado', 
                    f"Pagamento aprovado via {pagamento.metodo.nome}."
                )
        
        # Salvar as alterações
        pagamento.save()
        
        return JsonResponse({
            'status': 'sucesso',
            'mensagem': 'Status do pagamento atualizado com sucesso',
            'novo_status': pagamento.get_status_display(),
            'data_atualizacao': pagamento.data_processamento.strftime('%d/%m/%Y %H:%M')
        })
    
    return JsonResponse({'status': 'erro', 'mensagem': 'Método não permitido'}, status=405)

def adicionar_observacao_pedido(request, pk):
    """
    View para adicionar observações a um pedido
    """
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, pk=pk)
        observacao = request.POST.get('observacao', '')
        importante = request.POST.get('importante') == 'on'
        notificar_equipe = request.POST.get('notificar_equipe') == 'on'
        
        if not observacao:
            messages.error(request, "Por favor, digite uma observação.")
            return redirect('administracao:pedido_detalhe', pk=pk)
        
        # Formatação da observação com data/hora
        timestamp = timezone.now().strftime('%d/%m/%Y %H:%M')
        prefixo = "[IMPORTANTE] " if importante else ""
        nova_observacao = f"{prefixo}[{timestamp}] {observacao}"
        
        # Adicionar à observação existente ou criar nova
        if pedido.observacoes:
            pedido.observacoes += f"\n\n{nova_observacao}"
        else:
            pedido.observacoes = nova_observacao
            
        pedido.save()
        
        # Lógica para notificar equipe de logística (implementação depende do seu sistema)
        if notificar_equipe:
            # Aqui você pode adicionar código para enviar e-mails, notificações, etc.
            # Por exemplo:
            # enviar_notificacao_equipe(pedido, observacao)
            pass
        
        messages.success(request, "Observação adicionada com sucesso.")
        return redirect('administracao:pedido_detalhe', pk=pk)
        
    return redirect('administracao:pedido_detalhe', pk=pk)