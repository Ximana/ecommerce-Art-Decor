from django import template
from apps.usuarios.models import ListaDesejo

register = template.Library()

@register.filter
def na_lista_desejos(produto, usuario):
    """Verifica se um produto está na lista de desejos do usuário"""
    if not usuario.is_authenticated:
        return False
    return ListaDesejo.objects.filter(usuario=usuario, produto=produto).exists()