#/apps/administracao/views.py
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from apps.usuarios.models import Usuario
from apps.produtos.models import Produto, Categoria
from apps.pedidos.models import Pedido, ItemPedido
from apps.usuarios.forms import UsuarioRegistroForm #, UsuarioEdicaoForm
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q, Sum, Count, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from django.http import JsonResponse
from django.db.models.functions import TruncDay
from datetime import datetime, timedelta, date
import json


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #messages.success(request, 'Login realizado com sucesso!')
            return redirect('administracao:home')
        else:
            messages.error(request, 'Usuário ou senha inválidos')
    return render(request, 'administracao/login.html')

@login_required
def logout_view(request):
    logout(request)
    #messages.success(request, 'Logout realizado com sucesso!')
    return redirect('administracao:login')

@login_required
def home_view(request):
    return render(request, 'administracao/dashboard/home.html')

"""
class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'administracao/dashboard/home.html'
"""

class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'administracao/dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        hoje = timezone.localtime(timezone.now()).date()
        ontem = hoje - timedelta(days=1)
        inicio_mes = hoje.replace(day=1)
        ultimos_7_dias = hoje - timedelta(days=6)
        
        # Estatísticas gerais
        context.update(self.get_estatisticas_gerais(hoje, ontem, inicio_mes))
        
        # Dados para o gráfico de vendas dos últimos 7 dias
        context['dados_vendas'] = self.get_dados_vendas(ultimos_7_dias, hoje)
        
        # Últimos 5 pedidos
        context['ultimos_pedidos'] = self.get_ultimos_pedidos()
        
        # Produtos com estoque crítico
        context['produtos_estoque_critico'] = self.get_produtos_estoque_critico()
        
        # Dados para o gráfico de produtos por categoria
        context['dados_produtos_categoria'] = self.get_dados_produtos_categoria()
        
        # Estatísticas de produtos
        context['estatisticas_produtos'] = self.get_estatisticas_produtos()
        
        return context
    
    def get_estatisticas_gerais(self, hoje, ontem, inicio_mes):
        """Obtém estatísticas gerais para os cards do dashboard"""
        # Vendas de hoje - apenas pedidos com status 'entregue'
        vendas_hoje = Pedido.objects.filter(
            data_pedido__date=hoje,
            status='entregue'
        ).aggregate(total=Sum('valor_total'))
        
        vendas_ontem = Pedido.objects.filter(
            data_pedido__date=ontem,
            status='entregue'
        ).aggregate(total=Sum('valor_total'))
        
        # Calcular a variação percentual
        valor_hoje = vendas_hoje['total'] or 0
        valor_ontem = vendas_ontem['total'] or 1  # Evitar divisão por zero
        variacao_vendas = ((valor_hoje - valor_ontem) / valor_ontem) * 100 if valor_ontem > 0 else 0
        
        # Pedidos novos de hoje - continua considerando todos os pedidos, não apenas os entregues
        pedidos_hoje = Pedido.objects.filter(data_pedido__date=hoje).count()
        pedidos_ontem = Pedido.objects.filter(data_pedido__date=ontem).count()
        variacao_pedidos = ((pedidos_hoje - pedidos_ontem) / pedidos_ontem) * 100 if pedidos_ontem > 0 else 0
        
        # Total de clientes
        total_clientes = Usuario.objects.filter(tipo_usuario='cliente').count()
        
        # Clientes novos este mês
        clientes_novos_mes = Usuario.objects.filter(
            tipo_usuario='cliente',
            data_cadastro__date__gte=inicio_mes
        ).count()
        
        # Calcular taxa de conversão (pedidos entregues / visitantes únicos)
        # Como não temos modelo de visitantes, vamos usar uma estimativa baseada em usuários e pedidos entregues
        pedidos_entregues_mes = Pedido.objects.filter(
            data_pedido__date__gte=inicio_mes,
            status='entregue'
        ).count()
        usuarios_ativos = Usuario.objects.filter(ultimo_acesso__date__gte=inicio_mes).count()
        
        taxa_conversao = (pedidos_entregues_mes / usuarios_ativos * 100) if usuarios_ativos > 0 else 0
        
        # Comparar com a taxa do dia anterior
        usuarios_ativos_ontem = Usuario.objects.filter(ultimo_acesso__date=ontem).count()
        pedidos_entregues_ontem = Pedido.objects.filter(
            data_pedido__date=ontem,
            status='entregue'
        ).count()
        taxa_ontem = (pedidos_entregues_ontem / usuarios_ativos_ontem * 100) if usuarios_ativos_ontem > 0 else 0
        
        variacao_taxa = taxa_conversao - taxa_ontem
        
        return {
            'vendas_hoje': valor_hoje,
            'variacao_vendas': round(variacao_vendas, 1),
            'variacao_vendas_abs': round(abs(variacao_vendas), 1),
            'pedidos_novos': pedidos_hoje,
            'variacao_pedidos': round(variacao_pedidos, 1),
            'variacao_pedidos_abs': round(abs(variacao_pedidos), 1),
            'total_clientes': total_clientes,
            'clientes_novos_mes': clientes_novos_mes,
            'variacao_clientes': round((clientes_novos_mes / total_clientes * 100) if total_clientes > 0 else 0, 1),
            'variacao_clientes_abs': round(abs((clientes_novos_mes / total_clientes * 100) if total_clientes > 0 else 0), 1),
            'taxa_conversao': round(taxa_conversao, 1),
            'variacao_taxa': round(variacao_taxa, 1),
            'variacao_taxa_abs': round(abs(variacao_taxa), 1),
        }
    
    def get_dados_vendas(self, data_inicial, data_final):
        """Obtém dados de vendas para o gráfico"""
        # Buscar vendas agrupadas por dia - apenas pedidos 'entregue'
        vendas_por_dia = Pedido.objects.filter(
            data_pedido__date__gte=data_inicial,
            data_pedido__date__lte=data_final,
            status='entregue'
        ).annotate(
            dia=TruncDay('data_pedido')
        ).values('dia').annotate(
            total=Sum('valor_total')
        ).order_by('dia')
        
        # Formatar dados para o gráfico
        labels = []
        data = []
        
        # Preencher array com todos os dias no intervalo, mesmo sem vendas
        current_date = data_inicial
        date_dict = {x['dia'].date(): x['total'] for x in vendas_por_dia}
        
        while current_date <= data_final:
            labels.append(current_date.strftime('%d/%m'))
            data.append(float(date_dict.get(current_date, 0)))
            current_date += timedelta(days=1)
        
        return {
            'labels': json.dumps(labels),
            'data': json.dumps(data)
        }
    
    def get_ultimos_pedidos(self):
        """Obtém os últimos 5 pedidos"""
        return Pedido.objects.all().order_by('-data_pedido')[:5]
    
    def get_produtos_estoque_critico(self):
        """Obtém produtos com estoque abaixo ou igual ao mínimo"""
        return Produto.objects.filter(
            Q(estoque__lte=F('estoque_minimo')) & 
            Q(status=True)
        ).order_by('estoque')[:4]
    
    def get_dados_produtos_categoria(self):
        """Obtém dados de produtos por categoria para o gráfico"""
        categorias = Categoria.objects.annotate(
            total_produtos=Count('produtos', filter=Q(produtos__status=True))
        ).filter(total_produtos__gt=0).order_by('-total_produtos')[:5]
        
        # Formatar dados para o gráfico
        labels = [categoria.nome for categoria in categorias]
        data = [categoria.total_produtos for categoria in categorias]
        
        # Cores para o gráfico (mantendo as mesmas do template)
        cores = ['#198754', '#0dcaf0', '#ffc107', '#6c757d', '#dc3545']
        
        return {
            'labels': json.dumps(labels),
            'data': json.dumps(data),
            'cores': json.dumps(cores)
        }
    
    def get_estatisticas_produtos(self):
        """Obtém estatísticas gerais sobre produtos"""
        total_estoque = Produto.objects.filter(status=True).aggregate(total=Sum('estoque'))['total'] or 0
        total_categorias = Categoria.objects.filter(
            produtos__isnull=False, 
            produtos__status=True
        ).distinct().count()
        total_produtos = Produto.objects.filter(status=True).count()
        
        return {
            'total_estoque': total_estoque,
            'total_categorias': total_categorias,
            'total_produtos': total_produtos
        }