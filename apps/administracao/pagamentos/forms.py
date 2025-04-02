from django import forms
from apps.pagamentos.models import MetodoPagamento

class MetodoPagamentoForm(forms.ModelForm):
    class Meta:
        model = MetodoPagamento
        fields = ['nome', 'descricao', 'taxa', 'prazo_processamento', 'status']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'taxa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prazo_processamento': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }