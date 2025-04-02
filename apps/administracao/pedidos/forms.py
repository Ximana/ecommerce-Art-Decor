from django import forms
from apps.pedidos.models import FormaEnvio

class FormaEnvioForm(forms.ModelForm):
    class Meta:
        model = FormaEnvio
        fields = ['nome', 'descricao', 'prazo_entrega', 'taxa_fixa', 'status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionando classes bootstrap para os campos
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # O campo status é um checkbox, então precisa de tratamento diferente
        self.fields['status'].widget.attrs.update({'class': 'form-check-input'})