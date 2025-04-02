# apps/carrinhos/context_processors.py
from .models import Carrinho

def carrinho_contador(request):
    """
    Processador de contexto que disponibiliza a contagem de itens
    do carrinho para todos os templates.
    """
    quantidade_itens = 0
    
    # Para usuários logados, busca o carrinho associado ao usuário
    if request.user.is_authenticated:
        carrinho = Carrinho.objects.filter(usuario=request.user).first()
        if carrinho:
            quantidade_itens = carrinho.quantidade_total_itens()
    # Para usuários não logados, verifica se há um token no cookie
    else:
        token = request.COOKIES.get('carrinho_token')
        if token:
            carrinho = Carrinho.objects.filter(token=token).first()
            if carrinho:
                quantidade_itens = carrinho.quantidade_total_itens()
    
    return {
        'quantidade_itens_carrinho': quantidade_itens
    }