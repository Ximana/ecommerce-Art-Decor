from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django import forms

from .models import Pedido, ItemPedido, HistoricoPedido
from apps.pagamentos.models import MetodoPagamento, Pagamento


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ['produto', 'variacao', 'quantidade', 'preco_unitario', 'preco_total']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

class HistoricoPedidoInline(admin.TabularInline):
    model = HistoricoPedido
    extra = 0
    readonly_fields = ['status', 'data_alteracao', 'comentario']
    can_delete = False
    ordering = ['-data_alteracao']
    
    def has_add_permission(self, request, obj=None):
        return False

class PagamentosPedidoInline(admin.TabularInline):
    model = Pagamento
    verbose_name = 'Pagamento'
    verbose_name_plural = 'Pagamentos'
    extra = 0
    readonly_fields = [
        'metodo', 'valor_base', 'valor_taxa', 'valor', 
        'status_pagamento', 'data_pagamento', 'ver_comprovante'
    ]
    fields = [
        'metodo', 'valor_base', 'valor_taxa', 'valor', 
        'status_pagamento', 'data_pagamento', 'ver_comprovante'
    ]
    can_delete = False
    
    def status_pagamento(self, obj):
        cores = {
            'pendente': 'orange',
            'aprovado': 'green',
            'recusado': 'red',
            'estornado': 'purple'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold">{}</span>',
            cores.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_pagamento.short_description = 'Status'
    
    def ver_comprovante(self, obj):
        if obj.comprovante:
            return format_html(
                '<a href="{}" target="_blank">Ver Comprovante</a>',
                obj.comprovante.url
            )
        return '-'
    ver_comprovante.short_description = 'Comprovante'
    
    def has_add_permission(self, request, obj=None):
        return False

class AdicionarPagamentoForm(forms.Form):
    
    
    metodo_pagamento = forms.ModelChoiceField(
        queryset=MetodoPagamento.objects.filter(status=True),
        label='Método de Pagamento'
    )
    
    valor = forms.DecimalField(
        label='Valor (AOA)',
        min_value=0,
        decimal_places=2
    )
    codigo_transacao = forms.CharField(
        label='Código da Transação',
        required=False
    )
    detalhes = forms.CharField(
        label='Detalhes',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_pedido', 'cliente_nome', 'valor_total_formatado', 'data_pedido_formatada', 
        'status_colorido', 'status_pagamento'
    ]
    list_filter = ['status', 'data_pedido', 'metodo_pagamento']
    search_fields = ['codigo_pedido', 'usuario__email', 'usuario__nome']
    readonly_fields = [
        'codigo_pedido', 'usuario', 'endereco_entrega', 'endereco_cobranca',
        'data_pedido', 'subtotal', 'valor_frete', 'valor_desconto', 'valor_total',
        'taxa_pagamento', 'info_pagamento'
    ]
    fieldsets = (
        ('Informações do Pedido', {
            'fields': (
                'codigo_pedido', 'status', 'data_pedido', 'usuario',
                'endereco_entrega', 'endereco_cobranca'
            )
        }),
        ('Valores', {
            'fields': (
                'subtotal', 'valor_frete', 'valor_desconto', 'taxa_pagamento', 'valor_total'
            )
        }),
        ('Pagamento e Entrega', {
            'fields': (
                'metodo_pagamento', 'info_pagamento', 'forma_envio', 'observacoes'
            )
        }),
    )
    inlines = [ItemPedidoInline, PagamentosPedidoInline, HistoricoPedidoInline]
    
    def cliente_nome(self, obj):
        return obj.usuario.nome if hasattr(obj.usuario, 'nome') else obj.usuario.email
    cliente_nome.short_description = 'Cliente'
    
    def valor_total_formatado(self, obj):
        return f'AOA {obj.valor_total:,.2f}'.replace(',', '.')
    valor_total_formatado.short_description = 'Valor Total'
    
    def data_pedido_formatada(self, obj):
        return obj.data_pedido.strftime('%d/%m/%Y %H:%M')
    data_pedido_formatada.short_description = 'Data do Pedido'
    
    def status_colorido(self, obj):
        cores = {
            'aguardando_pagamento': 'orange',
            'pagamento_aprovado': 'blue',
            'em_separacao': 'purple',
            'em_transporte': 'teal',
            'entregue': 'green',
            'cancelado': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold">{}</span>',
            cores.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colorido.short_description = 'Status'
    
    def status_pagamento(self, obj):
        pagamento = obj.pagamentos.last()
        if not pagamento:
            return format_html('<span style="color: gray">Sem pagamento</span>')
        
        cores = {
            'pendente': 'orange',
            'aprovado': 'green',
            'recusado': 'red',
            'estornado': 'purple'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold">{}</span>',
            cores.get(pagamento.status, 'black'),
            pagamento.get_status_display()
        )
    status_pagamento.short_description = 'Pagamento'
    
    def info_pagamento(self, obj):
        pagamentos = obj.pagamentos.all()
        if not pagamentos:
            return "Nenhum pagamento registrado"
        
        html = "<ul>"
        for p in pagamentos:
            status_color = {
                'pendente': 'orange',
                'aprovado': 'green',
                'recusado': 'red',
                'estornado': 'purple'
            }.get(p.status, 'black')
            
            html += format_html(
                '<li><b>{}:</b> AOA {:,.2f} - <span style="color: {}">{}</span> - {}',
                p.metodo.nome,
                p.valor,
                status_color,
                p.get_status_display(),
                p.data_pagamento.strftime('%d/%m/%Y %H:%M') if p.data_pagamento else 'Data não informada'
            )
            
            if p.confirmado_por:
                html += format_html(' (confirmado por {})', p.confirmado_por)
            
            html += '</li>'
        
        html += "</ul>"
        
        # Botão para adicionar pagamento manual
        adicionar_url = reverse('admin:adicionar_pagamento_manual', args=[obj.id])
        html += format_html(
            '<a href="{}" class="button">Adicionar Pagamento Manual</a>',
            adicionar_url
        )
        
        return format_html(html)
    info_pagamento.short_description = 'Informações de Pagamento'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pedido_id>/adicionar-pagamento/',
                self.admin_site.admin_view(self.adicionar_pagamento_manual),
                name='adicionar_pagamento_manual'
            ),
        ]
        return custom_urls + urls
    
    def adicionar_pagamento_manual(self, request, pedido_id):
        from django.shortcuts import render, get_object_or_404, redirect
        from django.contrib import messages
        from django.utils import timezone
        from pagamentos.models import Pagamento, MetodoPagamento
        
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        if request.method == 'POST':
            form = AdicionarPagamentoForm(request.POST)
            if form.is_valid():
                metodo = form.cleaned_data['metodo_pagamento']
                valor_base = form.cleaned_data['valor']
                
                # Calcular a taxa baseada no método de pagamento
                valor_taxa = metodo.get_taxa_total(valor_base)
                valor_total = valor_base + valor_taxa
                
                # Criar o pagamento
                pagamento = Pagamento(
                    pedido=pedido,
                    metodo=metodo,
                    valor_base=valor_base,
                    valor_taxa=valor_taxa,
                    valor=valor_total,
                    status='aprovado',
                    fonte_confirmacao='admin',
                    confirmado_por=request.user,
                    data_pagamento=timezone.now(),
                    data_confirmacao=timezone.now(),
                    codigo_transacao=form.cleaned_data['codigo_transacao'],
                    detalhes_pagamento=form.cleaned_data['detalhes']
                )
                pagamento.save()
                
                # Atualizar o status do pedido
                pedido.atualizar_status_apos_pagamento()
                
                messages.success(request, f"Pagamento de AOA {valor_total:,.2f} adicionado com sucesso ao pedido {pedido.codigo_pedido}")
                return redirect('admin:pedidos_pedido_change', pedido_id)
        else:
            # Valor padrão é o valor total do pedido
            form = AdicionarPagamentoForm(initial={'valor': pedido.valor_total})
        
        context = {
            'form': form,
            'pedido': pedido,
            'title': f'Adicionar Pagamento Manual - Pedido {pedido.codigo_pedido}',
            'opts': self.model._meta,
        }
        return render(request, 'admin/pagamentos/adicionar_pagamento_manual.html', context)