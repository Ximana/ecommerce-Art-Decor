#apps/pagamentos/urls-py
from django.urls import path
from . import views

app_name = 'pagamentos'

urlpatterns = [
    
    path('enviar-comprovante/<str:codigo>/', views.EnviarComprovantePagamentoView.as_view(), name='enviar_comprovante'),
    
    #path('anexar-comprovante/<str:codigo_pedido>/', views.AnexarComprovanteView.as_view(), name='anexar_comprovante'),
    #path('confirmar-pagamento/<int:pagamento_id>/', views.confirmar_pagamento_cliente, name='confirmar_pagamento_cliente'),
    #path('pagamentos-pedido/<str:codigo_pedido>/', views.pagamentos_pedido, name='pagamentos_pedido'),
]
