#/apps/administracao/pagamentos/views_pagamentos.py
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from apps.pagamentos.models import MetodoPagamento
from .forms import MetodoPagamentoForm

class MetodoPagamentoListView(LoginRequiredMixin, ListView):
    model = MetodoPagamento
    template_name = 'administracao/pagamentos/listarMetodoPagamento.html'
    context_object_name = 'metodos_pagamento'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        tipo_filter = self.request.GET.get('tipo', '')
        
        if search_query:
            queryset = queryset.filter(nome__icontains=search_query)
            
        if tipo_filter and tipo_filter != 'todos':
            queryset = queryset.filter(tipo=tipo_filter)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MetodoPagamentoForm()
        context['search_query'] = self.request.GET.get('search', '')
        context['tipo_filter'] = self.request.GET.get('tipo', '')
        context['tipo_choices'] = MetodoPagamento.TIPO_CHOICES
        return context
    
    def post(self, request, *args, **kwargs):
        form = MetodoPagamentoForm(request.POST, request.FILES)
        if form.is_valid():
            metodo = form.save()
            messages.success(request, f'Método de pagamento "{metodo.nome}" cadastrado com sucesso!')
            return redirect('administracao:metodo_pagamento_lista')
        
        # Se o formulário não for válido, retorna à lista com os erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        messages.error(request, 'Erro ao cadastrar método de pagamento. Verifique os dados informados.')
        return self.render_to_response(context)


class MetodoPagamentoDetailView(LoginRequiredMixin, DetailView):
    model = MetodoPagamento
    template_name = 'administracao/pagamentos/detalheMetodoPagamento.html'
    context_object_name = 'metodo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MetodoPagamentoForm(instance=self.object)
        return context


class MetodoPagamentoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = MetodoPagamento
    form_class = MetodoPagamentoForm
    template_name = 'administracao/pagamentos/editarMetodoPagamento.html'
    success_url = reverse_lazy('administracao:metodo_pagamento_lista')
    success_message = "Método de pagamento atualizado com sucesso!"

    def form_valid(self, form):
        # Verificar se há uma imagem no formulário
        if 'imagem' in self.request.FILES:
            # Se houver uma imagem antiga e uma nova, remova a antiga
            if form.instance.imagem and form.cleaned_data.get('imagem') != form.instance.imagem:
                form.instance.imagem.delete(save=False)
        
        #messages.success(self.request, f'Método de pagamento "{form.instance.nome}" atualizado com sucesso!')
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            messages.error(request, 'Erro ao atualizar método de pagamento. Verifique os dados informados.')
            return self.form_invalid(form)

class MetodoPagamentoDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = MetodoPagamento
    success_url = reverse_lazy('administracao:metodo_pagamento_lista')
    success_message = "Método de pagamento removido com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        metodo = self.get_object()
        
        # Excluir a imagem se existir
        if metodo.imagem:
            metodo.imagem.delete()
            
        messages.success(self.request, f'Método de pagamento "{metodo.nome}" removido com sucesso!')
        return super().delete(request, *args, **kwargs)