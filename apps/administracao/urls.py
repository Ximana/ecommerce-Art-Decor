#apps/administracao/urls-py
from django.urls import path

from .usuarios import views_usuarios
from .produtos import views_produtos
from .pagamentos import views_pagamentos
from .pedidos import views_pedidos
from . import views

app_name = 'administracao'

urlpatterns = [
    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    
    # Produtos
    path('listaProdutos/', views_produtos.ProdutoListView.as_view(), name='listaProdutos'),
    path('produto/detalhe/<int:pk>/', views_produtos.ProdutoDetailView.as_view(), name='produto_detalhe'),
    path('produto/remover/<int:pk>/', views_produtos.ProdutoDeleteView.as_view(), name='produto_remover'),
    path('produto/editar/<int:pk>/', views_produtos.ProdutoUpdateView.as_view(), name='produto_editar'),
     
    # Marcas
    path('marcas/', views_produtos.MarcaListView.as_view(), name='marca_lista'),
    #path('marcas/editar/<int:pk>/', views_produtos.MarcaUpdateView.as_view(), name='marca_editar'),
    path('marcas/remover/<int:pk>/', views_produtos.MarcaDeleteView.as_view(), name='marca_remover'),
    

    # Categorias
    path('categorias/', views_produtos.CategoriaListView.as_view(), name='categoria_lista'),
    #path('categorias/editar/<int:pk>/', views_produtos.CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categorias/remover/<int:pk>/', views_produtos.CategoriaDeleteView.as_view(), name='categoria_remover'),
    
    # Usuarios
    path('usuarios/lista/', views_usuarios.UsuarioListView.as_view(), name='usuarios_lista'),
    path('usuarios/detalhe/<int:pk>/', views_usuarios.UsuarioDetailView.as_view(), name='usuario_detalhe'),
    path('usuarios/remover/<int:pk>/', views_usuarios.UsuarioDeleteView.as_view(), name='usuario_remover'),
    path('usuarios/atualizar/', views_usuarios.UsuarioUpdateView.as_view(), name='usuario_atualizar'),    
    path('usuario/foto/atualizar/', views_usuarios.AtualizarFotoView.as_view(), name='usuario_atualizar_foto'),
    path('usuario/senha/alterar/', views_usuarios.AlterarSenhaView.as_view(), name='usuario_alterar_senha'),
    #path('produto/editar/<int:pk>/', views_produtos.ProdutoUpdateView.as_view(), name='produto_editar'),
    
    # Pagamento
    path('metodos-pagamento/', views_pagamentos.MetodoPagamentoListView.as_view(), name='metodo_pagamento_lista'),
    path('metodos-pagamento/editar/<int:pk>/', views_pagamentos.MetodoPagamentoUpdateView.as_view(), name='metodo_pagamento_editar'),
    path('metodos-pagamento/remover/<int:pk>/', views_pagamentos.MetodoPagamentoDeleteView.as_view(), name='metodo_pagamento_remover'),
    
    # Pedidos
    
    # Pedidos - FormaEnvio
    path('formas-envio/', views_pedidos.FormaEnvioListView.as_view(), name='forma_envio_lista'),
    path('formas-envio/editar/<int:pk>/', views_pedidos.FormaEnvioUpdateView.as_view(), name='forma_envio_editar'),
    path('formas-envio/remover/<int:pk>/', views_pedidos.FormaEnvioDeleteView.as_view(), name='forma_envio_remover'),
    
]
