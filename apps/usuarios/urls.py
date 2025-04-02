#apps/usuarios/urls-py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticacao
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    
    # Lista de Desejos
    #path('listaDesejos/', views.listaDesejos_view, name='listaDesejos'),
    path('lista-desejos/', views.ListaDesejoView.as_view(), name='lista_desejos'),
    path('lista-desejos/adicionar/', views.AdicionarListaDesejoView.as_view(), name='adicionar_desejo'),
    path('lista-desejos/remover/<int:pk>/', views.RemoverListaDesejoView.as_view(), name='remover_desejo'),
    
    # Endereços
    path('enderecos/', views.EnderecoListView.as_view(), name='listar_enderecos'),
    path('enderecos/<int:pk>/editar/', views.EnderecoUpdateView.as_view(), name='editar_endereco'),
    path('enderecos/<int:pk>/excluir/', views.EnderecoDeleteView.as_view(), name='excluir_endereco'),
    path('enderecos/<int:pk>/principal/', views.definir_endereco_principal, name='endereco_principal'),

]
