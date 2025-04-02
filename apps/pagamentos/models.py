# File: apps/pagamentos/models.py
from django.db import models

class MetodoPagamento(models.Model):
    nome = models.CharField(
        'Nome', 
        max_length=50
    )
    
    descricao = models.TextField(
        'Descrição',
        blank=True,
        null=True
    )
    
    taxa = models.DecimalField(
        'Taxa',
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    prazo_processamento = models.IntegerField(
        'Prazo de Processamento (dias)',
        default=0
    )
    
    status = models.BooleanField(
        'Ativo',
        default=True
    )

    class Meta:
        verbose_name = 'Método de Pagamento'
        verbose_name_plural = 'Métodos de Pagamento'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Pagamento(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
        ('estornado', 'Estornado')
    )

    # Use a string reference instead of direct import
    pedido = models.ForeignKey(
        'pedidos.Pedido', 
        on_delete=models.CASCADE,
        related_name='pagamentos'
    )
    
    metodo = models.ForeignKey(
        MetodoPagamento, 
        on_delete=models.PROTECT
    )
    
    valor = models.DecimalField(
        'Valor',
        max_digits=10,
        decimal_places=2
    )
    
    status = models.CharField(
        'Status do Pagamento',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    
    codigo_transacao = models.CharField(
        'Código da Transação',
        max_length=100,
        blank=True,
        null=True
    )
    
    data_pagamento = models.DateTimeField(
        'Data do Pagamento',
        blank=True,
        null=True
    )
    
    data_processamento = models.DateTimeField(
        'Data do Processamento',
        blank=True,
        null=True
    )
    
    detalhes_pagamento = models.TextField(
        'Detalhes do Pagamento',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-data_processamento']

    def __str__(self):
        return f"Pagamento {self.pedido.codigo_pedido} - {self.get_status_display()}"