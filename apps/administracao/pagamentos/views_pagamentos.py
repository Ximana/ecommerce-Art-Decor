#/apps/administracao/pagamentos/views_pagamentos.py
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from apps.pagamentos.models import MetodoPagamento
from .forms import MetodoPagamentoForm

class MetodoPagamentoListView(ListView):
    model = MetodoPagamento
    template_name = 'administracao/pagamentos/listarMetodoPagamento.html'
    context_object_name = 'metodos_pagamento'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(nome__icontains=search_query)
        return queryset
    
    def post(self, request, *args, **kwargs):
        form = MetodoPagamentoForm(request.POST)
        if form.is_valid():
            metodo = form.save()
            messages.success(request, 'Método de pagamento cadastrado com sucesso!')
            return redirect('administracao:metodo_pagamento_lista')
        
        # Se o formulário não for válido, retorna à lista com os erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class MetodoPagamentoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = MetodoPagamento
    form_class = MetodoPagamentoForm
    template_name = 'administracao/pagamentos/editarMetodoPagamento.html'
    success_url = reverse_lazy('administracao:metodo_pagamento_lista')
    success_message = "Método de pagamento atualizado com sucesso!"

    def form_valid(self, form):
        messages.success(self.request, f'Método de pagamento "{form.instance.nome}" atualizado com sucesso!')
        return super().form_valid(form)


class MetodoPagamentoDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = MetodoPagamento
    success_url = reverse_lazy('administracao:metodo_pagamento_lista')
    success_message = "Método de pagamento removido com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)