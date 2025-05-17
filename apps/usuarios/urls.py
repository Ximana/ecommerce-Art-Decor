#apps/usuarios/urls-py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticacao
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('cadastro/', views.UsuarioCreateView.as_view(), name='cadastro'),
    path('usuarios/perfil//', views.UsuarioPerfilView.as_view(), name='perfil'),
    #path('usuarios/remover/<int:pk>/', views_usuarios.UsuarioDeleteView.as_view(), name='usuario_remover'),
    path('usuarios/atualizar/', views.UsuarioUpdateView.as_view(), name='atualizar_perfil'),    
    path('usuario/foto/atualizar/', views.AtualizarFotoView.as_view(), name='atualizar_foto'),
    path('usuario/senha/alterar/', views.AlterarSenhaView.as_view(), name='alterar_senha'),
    
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
