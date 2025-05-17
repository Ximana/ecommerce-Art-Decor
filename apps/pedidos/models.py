# apps/pedidos/models.py
from django.db import models
from apps.usuarios.models import Usuario
from apps.produtos.models import Produto
from django.urls import reverse
import uuid

class FormaEnvio(models.Model):
    OPCOES_ENVIO = [
        ('transportadora_local', 'Transportadora Local'),
        ('moto', 'Moto'),
        ('retirada_loja', 'Retirada na Loja'),
        ('entrega_rapida', 'Entrega Rápida (Mesmo Dia)'),
        ('entrega_economica', 'Entrega Económica'),
        ('outro', 'Outro'),
    ]
    
    nome = models.CharField(
        'Nome', 
        max_length=50,
        choices=OPCOES_ENVIO,
        default='outro'
    )
    
    descricao = models.TextField(
        'Descrição',
        blank=True,
        null=True
    )
    
    prazo_entrega = models.IntegerField(
        'Prazo de Entrega (dias)',
        blank=True,
        null=True
    )
    
    taxa_fixa = models.DecimalField(
        'Taxa Fixa de Envio',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    status = models.BooleanField(
        'Ativo',
        default=True
    )

    class Meta:
        verbose_name = 'Forma de Envio'
        verbose_name_plural = 'Formas de Envio'
        ordering = ['nome']

    def __str__(self):
        return self.get_nome_display()
        
    def get_absolute_url(self):
        return reverse('administracao:forma_envio_lista')

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('aguardando_pagamento', 'Aguardando Pagamento'),
        ('pagamento_aprovado', 'Pagamento Aprovado'),
        ('em_separacao', 'Em Separação'),
        ('em_transporte', 'Em Transporte'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado')
    )

    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    
    endereco_entrega = models.ForeignKey(
        'usuarios.Endereco', 
        on_delete=models.PROTECT,
        related_name='pedidos_entrega'
    )
    
    endereco_cobranca = models.ForeignKey(
        'usuarios.Endereco', 
        on_delete=models.PROTECT,
        related_name='pedidos_cobranca',
        blank=True,
        null=True
    )
    
    # Agora podemos usar FormaEnvio diretamente
    forma_envio = models.ForeignKey(
        FormaEnvio, 
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    
    # Ainda usamos string reference para MetodoPagamento
    metodo_pagamento = models.ForeignKey(
        'pagamentos.MetodoPagamento', 
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
 
    codigo_pedido = models.CharField(
        'Código do Pedido',
        max_length=20,
        unique=True
    )
    
    data_pedido = models.DateTimeField(
        'Data do Pedido',
        auto_now_add=True
    )
    
    subtotal = models.DecimalField(
        'Subtotal',
        max_digits=10,
        decimal_places=2
    )
    
    valor_frete = models.DecimalField(
        'Valor do Frete',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    valor_desconto = models.DecimalField(
        'Valor do Desconto',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    valor_total = models.DecimalField(
        'Valor Total',
        max_digits=10,
        decimal_places=2
    )
    
    status = models.CharField(
        'Status do Pedido',
        max_length=30,
        choices=STATUS_CHOICES,
        default='aguardando_pagamento'
    )
    
    observacoes = models.TextField(
        'Observações',
        blank=True,
        null=True
    )
    
    taxa_pagamento = models.DecimalField(
        'Taxa de Pagamento', 
        max_digits=10, 
        decimal_places=2, 
        default=0
    ) 
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_pedido']

    def __str__(self):
        return f"Pedido {self.codigo_pedido}"

    # Adicionar ao modelo Pedido um método para registrar histórico
    def registrar_status(self, status, comentario=None):
        """Registra uma mudança de status no histórico do pedido"""
        self.status = status
        self.save()
        
        return HistoricoPedido.objects.create(
            pedido=self,
            status=status,
            comentario=comentario
        )
        
    def atualizar_status_apos_pagamento(self):
        """
        Atualiza o status do pedido após confirmação de pagamento
        """
        # Verificar se existem pagamentos e se pelo menos um está aprovado
        pagamentos_total = self.pagamentos.count()
        
        if pagamentos_total > 0:
            pagamentos_aprovados = self.pagamentos.filter(status='aprovado').count()
            valor_pago = sum(p.valor for p in self.pagamentos.filter(status='aprovado'))
            
            # Se todos os pagamentos estão aprovados e o valor cobre o total
            if pagamentos_aprovados > 0 and valor_pago >= self.valor_total:
                if self.status == 'aguardando_pagamento':
                    self.registrar_status('pagamento_aprovado', 'Pagamento confirmado e aprovado.')
                    return True
        
        return False
     

    def save(self, *args, **kwargs):
        if not self.codigo_pedido:
            # Gera um código de pedido único
            self.codigo_pedido = f'PD-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

# Comentário da classe (mantido como referência)
"""
    promocao = models.ForeignKey(
        Promocao, 
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
"""

class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE,
        related_name='itens'
    )
    
    produto = models.ForeignKey(
        Produto, 
        on_delete=models.PROTECT,
        related_name='itens_pedido'
    )
    
    variacao = models.ForeignKey(
        'produtos.VariacaoProduto', 
        on_delete=models.PROTECT,
        related_name='itens_pedido',
        blank=True,
        null=True
    )
    
    quantidade = models.PositiveIntegerField(
        'Quantidade'
    )
    
    preco_unitario = models.DecimalField(
        'Preço Unitário',
        max_digits=10,
        decimal_places=2
    )
    
    preco_total = models.DecimalField(
        'Preço Total',
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

class HistoricoPedido(models.Model):
    STATUS_CHOICES = Pedido.STATUS_CHOICES

    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE,
        related_name='historico'
    )
    
    status = models.CharField(
        'Status',
        max_length=30,
        choices=STATUS_CHOICES
    )
    
    data_alteracao = models.DateTimeField(
        'Data da Alteração',
        auto_now_add=True
    )
    
    comentario = models.TextField(
        'Comentário',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Histórico de Pedido'
        verbose_name_plural = 'Históricos de Pedidos'
        ordering = ['-data_alteracao']

    def __str__(self):
        return f"Histórico {self.pedido.codigo_pedido} - {self.status}"