# apps/pedidos/forms.py
from django import forms
from apps.usuarios.models import Endereco

class EnderecoEntregaForm(forms.ModelForm):
    """
    Formulário para adição de um novo endereço durante o checkout
    """
    class Meta:
        model = Endereco
        fields = [
            'provincia', 'municipio', 'distrito', 'bairro', 
            'rua', 'casa', 'tipo', 'principal'
        ]
        widgets = {
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'distrito': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'casa': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

