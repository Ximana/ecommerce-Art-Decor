#apps/produtos/urls-py
from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    # Produtos
    path('lista/', views.ProdutoListView.as_view(), name='lista'),
    path('produto/detalhe/<int:pk>/', views.ProdutoDetailView.as_view(), name='detalhe'),
    
    # Avaliacoes
    path('avaliar/<int:produto_id>/', views.avaliar_produto, name='avaliar_produto'),
    path('remover-avaliacao/<int:avaliacao_id>/', views.remover_avaliacao, name='remover_avaliacao'),
    
]
