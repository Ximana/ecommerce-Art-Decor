#apps/produtos/urls-py
from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    #path('lista/', views.lista_view, name='lista'),
    #path('detalhe/', views.detalhe_view, name='detalhe'),
    
    path('lista/', views.ProdutoListView.as_view(), name='lista'),
    path('produto/detalhe/<int:pk>/', views.ProdutoDetailView.as_view(), name='detalhe'),
    
]
