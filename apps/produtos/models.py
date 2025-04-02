# apps/produtos/models.py

from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.db.models import Max
import uuid
import os

def produto_imagem_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join('produtos/', filename)

class Categoria(models.Model):
    nome = models.CharField(
        'Nome', 
        max_length=50
    )
    
    descricao = models.TextField(
        'Descrição',
        blank=True,
        null=True
    )
    
    categoria_pai = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        related_name='subcategorias',
        blank=True,
        null=True
    )
    
    imagem = models.ImageField(
        'Imagem',
        upload_to='categorias/',
        blank=True,
        null=True
    )
    
    status = models.BooleanField(
        'Ativo',
        default=True
    )

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Marca(models.Model):
    nome = models.CharField(
        'Nome', 
        max_length=50
    )
    
    descricao = models.TextField(
        'Descrição',
        blank=True,
        null=True
    )
    
    logo = models.ImageField(
        'Logo',
        upload_to='marcas/',
        blank=True,
        null=True
    )
    
    status = models.BooleanField(
        'Ativo',
        default=True
    )

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nome']

    def __str__(self):
        return self.nome
    
    #def get_absolute_url(self):
     #   return reverse("marca:detalhe", kwargs={"pk": self.pk})

class Produto(models.Model):
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.PROTECT,
        related_name='produtos'
    )
    
    marca = models.ForeignKey(
        Marca, 
        on_delete=models.SET_NULL,
        related_name='produtos',
        blank=True,
        null=True
    )
    
    nome = models.CharField(
        'Nome', 
        max_length=100
    )
    
    descricao = models.TextField(
        'Descrição',
        blank=True,
        null=True
    )
    
    preco_custo = models.DecimalField(
        'Preço de Custo',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    preco_venda = models.DecimalField(
        'Preço de Venda',
        max_digits=10,
        decimal_places=2
    )
    
    
    codigo_barras = models.CharField(
        'Código de Barras',
        max_length=50,
        blank=True,
        null=True
    )
    
    peso = models.DecimalField(
        'Peso',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    dimensoes = models.CharField(
        'Dimensões',
        max_length=50,
        blank=True,
        null=True
    )
    
    estoque = models.IntegerField(
        'Estoque',
        default=0
    )
    
    estoque_minimo = models.IntegerField(
        'Estoque Mínimo',
        default=5
    )
    
    destaque = models.BooleanField(
        'Produto em Destaque',
        default=False
    )
    
    data_cadastro = models.DateTimeField(
        'Data de Cadastro',
        auto_now_add=True
    )
    
    ultima_atualizacao = models.DateTimeField(
        'Última Atualização',
        auto_now=True
    )
    
    status = models.BooleanField(
        'Ativo',
        default=True
    )
    

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-destaque', 'nome']

    def __str__(self):
        return self.nome
    
    def get_absolute_url(self):
        return reverse("administracao:produto_detalhe", kwargs={"pk": self.pk})

class ImagemProduto(models.Model):
    produto = models.ForeignKey(
        Produto, 
        on_delete=models.CASCADE,
        related_name='imagens'
    )
    
    url_imagem = models.ImageField(
        'Imagem',
        upload_to=produto_imagem_path
    )
    
    ordem = models.IntegerField(
        'Ordem',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Imagem do Produto'
        verbose_name_plural = 'Imagens do Produto'
        ordering = ['ordem']

    def __str__(self):
        return f"Imagem de {self.produto.nome}"
    
    def save(self, *args, **kwargs):
        # Se ordem não foi especificada, determina a próxima ordem
        if self.ordem is None:
            # Busca a maior ordem atual para este produto
            max_ordem = ImagemProduto.objects.filter(produto=self.produto).aggregate(Max('ordem'))['ordem__max']
            
            # Se não existem imagens, começa com 1
            # Se existem imagens, adiciona 1 ao máximo atual
            self.ordem = 1 if max_ordem is None else max_ordem + 1
        
        super().save(*args, **kwargs)
        
class MovimentoEstoque(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('ajuste', 'Ajuste')
    ]

    produto = models.ForeignKey(
        Produto, 
        on_delete=models.CASCADE,
        related_name='movimentos_estoque'
    )
    
    quantidade = models.IntegerField('Quantidade')
    
    tipo = models.CharField(
        'Tipo de Movimento', 
        max_length=10, 
        choices=TIPO_CHOICES
    )
    
    data = models.DateTimeField(
        'Data do Movimento', 
        default=timezone.now
    )
    
    observacao = models.TextField(
        'Observação', 
        blank=True, 
        null=True
    )

    class Meta:
        verbose_name = 'Movimento de Estoque'
        verbose_name_plural = 'Movimentos de Estoque'
        ordering = ['-data']

    def __str__(self):
        return f"{self.produto.nome} - {self.get_tipo_display()} de {self.quantidade}"

    
    def save(self, *args, **kwargs):
        # Atualiza o estoque do produto
        if self.tipo == 'entrada':
            self.produto.estoque += self.quantidade
        elif self.tipo == 'saida':
            self.produto.estoque -= self.quantidade
        elif self.tipo == 'ajuste':
            # Para ajustes, assume-se que a quantidade já representa a mudança líquida
            # (positiva ou negativa) a ser aplicada ao estoque
            self.produto.estoque += self.quantidade  # Use += para permitir ajustes positivos e negativos
        
        self.produto.save()
        super().save(*args, **kwargs)
        
        
class VariacaoProduto(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='variacoes'
    )
    
    nome = models.CharField(
        'Nome da Variação',
        max_length=100
    )
    
    valor = models.DecimalField(
        'Valor Adicional',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    estoque = models.IntegerField(
        'Estoque da Variação',
        default=0
    )
    
    status = models.BooleanField(
        'Ativo',
        default=True
    )

    class Meta:
        verbose_name = 'Variação de Produto'
        verbose_name_plural = 'Variações de Produto'
        unique_together = ['produto', 'nome']

    def __str__(self):
        return f"{self.produto.nome} - {self.nome}"
    

class Avaliacao(models.Model):
    produto = models.ForeignKey(
        Produto, 
        on_delete=models.CASCADE,
        related_name='avaliacoes'
    )
    
    usuario = models.ForeignKey(
        'usuarios.Usuario',  # Use uma string para referência
        on_delete=models.CASCADE,
        related_name='avaliacoes'
    )
    
    nota = models.IntegerField(
        'Nota',
        choices=[(i, i) for i in range(1, 6)]
    )
    
    comentario = models.TextField(
        'Comentário',
        blank=True,
        null=True
    )
    
    data_avaliacao = models.DateTimeField(
        'Data da Avaliação',
        auto_now_add=True
    )
    
    status = models.BooleanField(
        'Ativo',
        default=True
    )

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        unique_together = ['produto', 'usuario']
        ordering = ['-data_avaliacao']

    def __str__(self):
        return f"Avaliação de {self.produto.nome} por {self.usuario.username}"

class Visita(models.Model):
    usuario = models.ForeignKey(
        'usuarios.Usuario',  # Use uma string para referência
        on_delete=models.SET_NULL,
        related_name='visitas',
        blank=True,
        null=True
    )
    
    produto = models.ForeignKey(
        Produto, 
        on_delete=models.CASCADE,
        related_name='visitas'
    )
    
    ip = models.CharField(
        'Endereço IP',
        max_length=45,
        blank=True,
        null=True
    )
    
    user_agent = models.TextField(
        'User Agent',
        blank=True,
        null=True
    )
    
    data_visita = models.DateTimeField(
        'Data da Visita',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Visita'
        verbose_name_plural = 'Visitas'
        ordering = ['-data_visita']

    def __str__(self):
        return f"Visita de {self.usuario.username if self.usuario else 'Anônimo'} - {self.produto.nome}"
