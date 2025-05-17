# apps/pagamentos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.utils import timezone
from .forms import ComprovantePagamentoForm
from .models import Pagamento
from apps.pedidos.models import Pedido

class EnviarComprovantePagamentoView(LoginRequiredMixin, View):
    """
    View para enviar comprovante de pagamento pelo cliente
    """
    login_url = '/usuarios/login/'
    
    def post(self, request, codigo, *args, **kwargs):
        pedido = get_object_or_404(Pedido, codigo_pedido=codigo, usuario=request.user, status='aguardando_pagamento')
        
        # Verificar se já existe um pagamento pendente para este pedido
        pagamento = Pagamento.objects.filter(pedido=pedido, status='pendente').first()
        
        # Se não existir, criar um novo pagamento
        if not pagamento:
            pagamento = Pagamento(
                pedido=pedido,
                metodo=pedido.metodo_pagamento,
                valor_base=pedido.valor_total - pedido.taxa_pagamento,
                valor_taxa=pedido.taxa_pagamento,
                valor=pedido.valor_total,
                status='pendente'
            )
            pagamento.save()
        
        form = ComprovantePagamentoForm(request.POST, request.FILES, instance=pagamento)
        if form.is_valid():
            pagamento = form.save(commit=False)
            pagamento.data_pagamento = timezone.now()
            pagamento.save()
            
            # Registrar no histórico do pedido
            pedido.registrar_status(
                pedido.status, 
                f"Comprovante de pagamento enviado pelo cliente. Aguardando confirmação."
            )
            
            messages.success(request, "Comprovante enviado com sucesso! Seu pagamento será confirmado em breve.")
        else:
            messages.error(request, "Erro ao enviar comprovante. Verifique os campos e tente novamente.")
        
        return redirect('pedidos:detalhe', codigo=pedido.codigo_pedido)