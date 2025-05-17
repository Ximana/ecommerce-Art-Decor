from django import forms
from apps.pagamentos.models import MetodoPagamento

class MetodoPagamentoForm(forms.ModelForm):
    class Meta:
        model = MetodoPagamento
        fields = [
            'nome', 'tipo', 'banco', 'numero_conta', 'iban', 'titular_conta',
            'descricao', 'instrucoes', 'taxa', 'taxa_fixa', 'valor_minimo',
            'valor_maximo', 'prazo_processamento', 'status', 'mostrar_na_loja',
            'imagem', 'ordem'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'banco': forms.Select(attrs={'class': 'form-select'}),
            'numero_conta': forms.TextInput(attrs={'class': 'form-control'}),
            'iban': forms.TextInput(attrs={'class': 'form-control'}),
            'titular_conta': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instrucoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'taxa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'taxa_fixa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_minimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_maximo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prazo_processamento': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mostrar_na_loja': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Marcar campos opcionais
        opcional_fields = ['banco', 'numero_conta', 'iban', 'titular_conta', 
                          'descricao', 'instrucoes', 'imagem']
        
        for field in opcional_fields:
            if field in self.fields:
                self.fields[field].required = False