# apps/pagamentos/models.py
from django.db import models

class MetodoPagamento(models.Model):
    TIPO_CHOICES = (
        ('transferencia_bancaria', 'Transferência Bancária'),
        ('multicaixa_express', 'Multicaixa Express'),
        ('dinheiro', 'Dinheiro na Entrega'),
        ('paypal', 'PayPal'),
        ('referencia', 'Referência Bancária'),
        ('outro', 'Outro'),
    )
    
    BANCO_CHOICES = (
        ('', '-- Selecione um Banco --'),
        ('bai', 'Banco Angolano de Investimentos (BAI)'),
        ('bfa', 'Banco de Fomento Angola (BFA)'),
        ('bic', 'Banco BIC'),
        ('bpc', 'Banco de Poupança e Crédito (BPC)'),
        ('atlantico', 'Banco Atlântico'),
        ('bda', 'Banco de Desenvolvimento de Angola (BDA)'),
        ('bni', 'Banco de Negócios Internacional (BNI)'),
        ('keve', 'Banco Keve'),
        ('sol', 'Banco Sol'),
        ('millennium', 'Millennium Atlântico'),
        ('outro', 'Outro'),
    )
    
    nome = models.CharField(
        'Nome', 
        max_length=50
    )
    
    tipo = models.CharField(
        'Tipo de Pagamento',
        max_length=50,
        choices=TIPO_CHOICES,
        default='transferencia_bancaria'
    )
    
    banco = models.CharField(
        'Banco',
        max_length=30,
        choices=BANCO_CHOICES,
        blank=True,
        null=True,
        help_text='Selecione o banco para métodos de pagamento bancário'
    )
    
    numero_conta = models.CharField(
        'Número da Conta',
        max_length=30,
        blank=True,
        null=True,
        help_text='Número da conta para transferências bancárias'
    )
    
    iban = models.CharField(
        'IBAN',
        max_length=50,
        blank=True,
        null=True,
        help_text='IBAN para transferências bancárias internacionais'
    )
    
    titular_conta = models.CharField(
        'Titular da Conta',
        max_length=100,
        blank=True,
        null=True
    )
    
    descricao = models.TextField(
        'Descrição',
        blank=True,
        null=True
    )
    
    instrucoes = models.TextField(
        'Instruções de Pagamento',
        blank=True,
        null=True,
        help_text='Instruções detalhadas sobre como utilizar este método de pagamento'
    )
    
    taxa = models.DecimalField(
        'Taxa',
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Taxa em percentagem (%) cobrada por este método de pagamento'
    )
    
    taxa_fixa = models.DecimalField(
        'Taxa Fixa',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Valor fixo (AOA) cobrado por este método de pagamento'
    )
    
    valor_minimo = models.DecimalField(
        'Valor Mínimo',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Valor mínimo (AOA) para aceitar este método de pagamento'
    )
    
    valor_maximo = models.DecimalField(
        'Valor Máximo',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Valor máximo (AOA) para aceitar este método de pagamento (0 = sem limite)'
    )
    
    prazo_processamento = models.IntegerField(
        'Prazo de Processamento (dias)',
        default=0
    )
    
    status = models.BooleanField(
        'Ativo',
        default=True
    )
    
    mostrar_na_loja = models.BooleanField(
        'Mostrar na Loja',
        default=True,
        help_text='Se este método deve aparecer como opção para clientes durante o checkout'
    )
    
    imagem = models.ImageField(
        'Imagem/Logo',
        upload_to='metodos_pagamento/',
        blank=True,
        null=True,
        help_text='Logo ou imagem do método de pagamento'
    )
    
    ordem = models.PositiveSmallIntegerField(
        'Ordem de Exibição',
        default=0,
        help_text='Ordem em que este método aparece na loja (menor = primeiro)'
    )
    
    data_criacao = models.DateTimeField(
        'Data de Criação',
        auto_now_add=True
    )
    
    data_atualizacao = models.DateTimeField(
        'Última Atualização',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Método de Pagamento'
        verbose_name_plural = 'Métodos de Pagamento'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome
    
    def get_taxa_total(self, valor):
        """
        Calcula a taxa total aplicada ao valor
        Taxa = (valor * taxa%) + taxa_fixa
        """
        taxa_percentual = (valor * self.taxa) / 100
        return taxa_percentual + self.taxa_fixa
    
    def get_valor_com_taxa(self, valor):
        """
        Retorna o valor total incluindo as taxas
        """
        return valor + self.get_taxa_total(valor)
    
    def is_valid_for_amount(self, valor):
        """
        Verifica se o método de pagamento é válido para o valor fornecido
        """
        if self.valor_minimo > 0 and valor < self.valor_minimo:
            return False
        if self.valor_maximo > 0 and valor > self.valor_maximo:
            return False
        return True
    
    def has_bank_details(self):
        """
        Verifica se o método de pagamento possui detalhes bancários
        """
        return self.tipo in ['transferencia_bancaria', 'referencia'] and self.banco and self.numero_conta

class Pagamento(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('recusado', 'Recusado'),
        ('estornado', 'Estornado')
    )
    
    FONTE_CONFIRMACAO = (
        ('admin', 'Administrador'),
        ('automatica', 'Automática'),
        ('bancaria', 'Confirmação Bancária'),
        ('cliente', 'Cliente'),
        ('api', 'API/Gateway'),
    )

    # Use a string reference instead of direct import
    pedido = models.ForeignKey(
        'pedidos.Pedido', 
        on_delete=models.CASCADE,
        related_name='pagamentos',
        verbose_name='Pedido'
    )
    
    metodo = models.ForeignKey(
        MetodoPagamento, 
        on_delete=models.PROTECT,
        verbose_name='Método de Pagamento'
    )
    
    valor_base = models.DecimalField(
        'Valor Base',
        max_digits=10,
        decimal_places=2,
        help_text='Valor original sem taxas'
    )
    
    valor_taxa = models.DecimalField(
        'Valor da Taxa',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Valor da taxa aplicada'
    )
    
    valor = models.DecimalField(
        'Valor Total',
        max_digits=10,
        decimal_places=2,
        help_text='Valor total com taxas incluídas'
    )
    
    comprovante = models.FileField(
        'Comprovante de Pagamento',
        upload_to='comprovantes_pagamento/%Y/%m/',
        blank=True,
        null=True
    )
    
    status = models.CharField(
        'Status do Pagamento',
        max_length=30,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    
    fonte_confirmacao = models.CharField(
        'Fonte de Confirmação',
        max_length=20,
        choices=FONTE_CONFIRMACAO,
        blank=True,
        null=True
    )
    
    codigo_transacao = models.CharField(
        'Código da Transação',
        max_length=100,
        blank=True,
        null=True
    )
    
    referencia_pagamento = models.CharField(
        'Referência do Pagamento',
        max_length=100,
        blank=True,
        null=True,
        help_text='Referência utilizada pelo cliente para realizar o pagamento'
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
    
    data_confirmacao = models.DateTimeField(
        'Data da Confirmação',
        blank=True,
        null=True
    )
    
    confirmado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='pagamentos_confirmados',
        verbose_name='Confirmado por'
    )
    
    observacoes_internas = models.TextField(
        'Observações Internas',
        blank=True,
        null=True,
        help_text='Observações internas visíveis apenas para os administradores'
    )
    
    detalhes_pagamento = models.TextField(
        'Detalhes do Pagamento',
        blank=True,
        null=True
    )
    
    data_criacao = models.DateTimeField(
        'Data de Criação',
        auto_now_add=True
    )
    
    data_atualizacao = models.DateTimeField(
        'Última Atualização',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-data_processamento', '-data_criacao']

    def __str__(self):
        return f"Pagamento {self.pedido.codigo_pedido} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Se o valor_base for definido mas não o valor com taxa, calcular automaticamente
        if self.valor_base and not self.valor:
            self.valor_taxa = self.metodo.get_taxa_total(self.valor_base)
            self.valor = self.valor_base + self.valor_taxa
        super().save(*args, **kwargs)
    
    def confirmar_pagamento(self, usuario=None, fonte='admin'):
        """
        Confirma o pagamento e atualiza o status
        """
        from django.utils import timezone
        
        # Só prosseguir se o status atual for pendente
        if self.status != 'aprovado':
            self.status = 'aprovado'
            self.data_confirmacao = timezone.now()
            
            # Se a data de processamento ainda não estiver definida, definir agora
            if not self.data_processamento:
                self.data_processamento = timezone.now()
                
            self.fonte_confirmacao = fonte
            if usuario:
                self.confirmado_por = usuario
            self.save()
            
            # Atualizar o status do pedido se necessário
            return self.pedido.atualizar_status_apos_pagamento()
        return False