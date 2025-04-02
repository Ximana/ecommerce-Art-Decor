#apps/usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
import uuid
import os

def usuario_foto_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join('usuarios/perfil', filename)

class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = (
        ('cliente', 'Cliente'),
        ('funcionario', 'Funcionario'),
        ('vendedor', 'Vendedor'),
        ('admin', 'Administrador'),       
        
    )

    # Campos adicionais de usuário
    bi = models.CharField(
        'Número do BI', 
        max_length=16, 
        unique=True, 
        null=True, 
        blank=True
    )
    
    telefone = models.CharField(
        'Telefone',
        max_length=15,
        blank=True,
        null=True
    )
    
    data_nascimento = models.DateField(
        'Data de Nascimento',
        null=True,
        blank=True
    )
    
    tipo_usuario = models.CharField(
        'Tipo de Usuário',
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='cliente'
    )
    
    foto_perfil = models.ImageField(
        'Foto de Perfil',
        upload_to=usuario_foto_path,
        blank=True,
        null=True
    )
    
    data_cadastro = models.DateTimeField(
        'Data de Cadastro',
        auto_now_add=True
    )
    
    ultimo_acesso = models.DateTimeField(
        'Último Acesso',
        null=True,
        blank=True
    )
    
    status = models.BooleanField(
        'Status',
        default=True
    )
    
    def get_nome_completo(self):
        """Retorna o nome completo do usuário."""
        return self.get_full_name() or self.username
    
    def is_admin(self):
        """Verifica se o usuário é um administrador."""
        return self.tipo_usuario == 'admin'
    
    

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name() or self.username

    def get_absolute_url(self):
        return reverse('administracao:usuario_detalhe', kwargs={'pk': self.pk})

class Endereco(models.Model):
    TIPO_ENDERECO_CHOICES = (
        ('entrega', 'Entrega'),
        ('cobranca', 'Cobrança'),
        ('ambos', 'Ambos')
    )

    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='enderecos'
    )
    
    tipo = models.CharField(
        'Tipo de Endereço',
        max_length=20,
        choices=TIPO_ENDERECO_CHOICES,
        default='entrega'
    )
    
    
    provincia = models.CharField(
        'Província',
        max_length=50
    )
    
    municipio = models.CharField(
        'Munícipio',
        max_length=50
    )
    
    distrito = models.CharField(
        'Distrito',
        max_length=50
    )    
    
    bairro = models.CharField(
        'Bairro',
        max_length=50
    )
    rua = models.CharField(
        'Rua',
        max_length=50
    )
    casa = models.CharField(
        'casa',
        max_length=50
    )    
    principal = models.BooleanField(
        'Endereço Principal',
        default=False
    )

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    
    def __str__(self):
        return f"{self.rua}, {self.casa} - {self.bairro}, {self.municipio}/{self.provincia}"


class ListaDesejo(models.Model):
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,
        related_name='lista_desejos'
    )
    
    produto = models.ForeignKey(
        'produtos.Produto',  # Use uma string para referência
        on_delete=models.CASCADE,
        related_name='lista_desejos'
    )
    
    data_adicao = models.DateTimeField(
        'Data de Adição',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Lista de Desejo'
        verbose_name_plural = 'Listas de Desejo'
        unique_together = ['usuario', 'produto']
        ordering = ['-data_adicao']

    def __str__(self):
        return f"{self.usuario.username} - {self.produto.nome}"