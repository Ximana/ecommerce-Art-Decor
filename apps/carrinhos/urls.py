#apps/carrinhos/urls-py
from django.urls import path
from . import views

app_name = 'carrinhos'

urlpatterns = [
    path('', views.CarrinhoListView.as_view(), name='lista'),
    path('adicionar/', views.AdicionarAoCarrinhoView.as_view(), name='adicionar'),
    path('atualizar-item/<int:pk>/', views.AtualizarItemCarrinhoView.as_view(), name='atualizar_item'),
    path('remover-item/<int:pk>/', views.RemoverItemCarrinhoView.as_view(), name='remover_item'),
]
