# apps/pagamentos/forms.py
from django import forms
from .models import Pagamento

class ComprovantePagamentoForm(forms.ModelForm):
    """
    Formulário para envio de comprovante de pagamento pelo cliente
    """
    class Meta:
        model = Pagamento
        fields = ['comprovante', 'detalhes_pagamento']
        widgets = {
            'comprovante': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*, application/pdf'}),
            'detalhes_pagamento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Informe detalhes adicionais sobre o pagamento (opcional)'}),
        }
        labels = {
            'comprovante': 'Comprovante de Pagamento',
            'detalhes_pagamento': 'Detalhes do Pagamento',
        }
        help_texts = {
            'comprovante': 'Envie uma imagem ou PDF do comprovante de transferência ou pagamento',
        }