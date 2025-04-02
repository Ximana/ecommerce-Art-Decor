#apps/carrinhos/models.py
from django.db import models
from django.conf import settings
from apps.produtos.models import Produto, VariacaoProduto
import uuid

class Carrinho(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='carrinhos',
        null=True,
        blank=True
    )
    
    token = models.CharField(
        'Token',
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text='Token para usuários não logados'
    )
    
    data_criacao = models.DateTimeField(
        'Data de Criação',
        auto_now_add=True
    )
    
    ultima_atualizacao = models.DateTimeField(
        'Última Atualização',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'
        ordering = ['-ultima_atualizacao']

    def __str__(self):
        return f"Carrinho {self.id} - {self.usuario or 'Anônimo'}"

    def save(self, *args, **kwargs):
        # Gera um token único para carrinhos de usuários não logados
        if not self.token and not self.usuario:
            self.token = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def calcular_total(self):
        """
        Calcula o valor total dos itens no carrinho
        """
        return sum(item.calcular_subtotal() for item in self.itens.all())

    def quantidade_total_itens(self):
        """
        Retorna a quantidade total de itens no carrinho
        """
        return sum(item.quantidade for item in self.itens.all())

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(
        Carrinho, 
        on_delete=models.CASCADE,
        related_name='itens'
    )
    
    variacao = models.ForeignKey(
        VariacaoProduto,  
        on_delete=models.CASCADE,
        related_name='itens_carrinho',
        null=True,
        blank=True
    )
    
    produto = models.ForeignKey(
        Produto, 
        on_delete=models.CASCADE,
        related_name='itens_carrinho'
    )
    
    
    quantidade = models.PositiveIntegerField(
        'Quantidade',
        default=1
    )
    
    data_adicao = models.DateTimeField(
        'Data de Adição',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'
        unique_together = ['carrinho', 'produto', 'variacao']

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

    def calcular_subtotal(self):
        """
        Calcula o subtotal do item considerando variação e quantidade
        """
        preco_base = self.produto.preco_venda
        
        # Adiciona o valor da variação, se existir
        if self.variacao:
            preco_base += self.variacao.valor
        
        return preco_base * self.quantidade

    def save(self, *args, **kwargs):
        # Validação de estoque
        if self.variacao:
            estoque_disponivel = self.variacao.estoque
        else:
            estoque_disponivel = self.produto.estoque

        if self.quantidade > estoque_disponivel:
            raise ValueError(f"Quantidade indisponível. Estoque atual: {estoque_disponivel}")

        super().save(*args, **kwargs)


