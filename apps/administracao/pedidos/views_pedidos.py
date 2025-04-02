from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from apps.pedidos.models import FormaEnvio
from .forms import FormaEnvioForm

class FormaEnvioListView(LoginRequiredMixin, ListView):
    model = FormaEnvio
    template_name = 'administracao/pedidos/formaEnvio/listaFormaEnvio.html'
    context_object_name = 'formas_envio'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(nome__icontains=search_query)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FormaEnvioForm()
        context['form_editar'] = FormaEnvioForm()
        context['search_query'] = self.request.GET.get('search', '')
        return context
    
    def post(self, request, *args, **kwargs):
        form = FormaEnvioForm(request.POST)
        if form.is_valid():
            forma_envio = form.save()
            messages.success(request, 'Forma de envio cadastrada com sucesso!')
            return redirect('administracao:forma_envio_lista')
        
        # Se o formulário não for válido, retorna à lista com os erros
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class FormaEnvioUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = FormaEnvio
    form_class = FormaEnvioForm
    template_name = 'administracao/pedidos/listaFormaEnvio.html'
    success_url = reverse_lazy('administracao:forma_envio_lista')
    success_message = "Forma de envio atualizada com sucesso!"
    
    def form_valid(self, form):
        messages.success(self.request, f'Forma de envio "{form.instance.get_nome_display()}" atualizada com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao atualizar forma de envio. Verifique os dados informados.')
        return redirect('administracao:forma_envio_lista')

class FormaEnvioDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = FormaEnvio
    success_url = reverse_lazy('administracao:forma_envio_lista')
    success_message = "Forma de envio removida com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)