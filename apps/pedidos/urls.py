# apps/pedidos/urls.py
from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('confirmacao/<str:codigo>/', views.ConfirmacaoPedidoView.as_view(), name='confirmacao'),
    path('meus-pedidos/', views.MeusPedidosView.as_view(), name='meus_pedidos'),
    path('detalhe/<str:codigo>/', views.DetalhePedidoView.as_view(), name='detalhe'),
    path('cancelar/<str:codigo>/', views.CancelarPedidoView.as_view(), name='cancelar'),
    path('confirmar-entrega/<str:codigo>/', views.ConfirmarEntregaPedidoView.as_view(), name='confirmar_entrega'),
    path('ajax/calcular-frete/', views.calcular_frete_ajax, name='calcular_frete_ajax'),
]