
from django import forms
from apps.produtos.models import Produto, Categoria, Marca, ImagemProduto, MovimentoEstoque

class ProdutoRegistroForm(forms.ModelForm):
    
    primeira_imagem = forms.ImageField(
        label='Primeira Imagem do Produto',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )
    
    class Meta:
        model = Produto
        fields = [
            'nome', 'descricao', 'categoria', 'marca', 
            'preco_custo', 'preco_venda', 'codigo_barras', 
            'peso', 'dimensoes', 'estoque', 'estoque_minimo', 
            'destaque', 'status'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'preco_custo': forms.NumberInput(attrs={'step': '0.01'}),
            'preco_venda': forms.NumberInput(attrs={'step': '0.01'}),
            'peso': forms.NumberInput(attrs={'step': '0.01'}),
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.filter(status=True)
        self.fields['marca'].queryset = Marca.objects.filter(status=True)
        
        # Adiciona classes Bootstrap para validação e estilo
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in ['destaque', 'status']:
                field.widget.attrs['class'] = 'form-check-input'
                
class ProdutoImageForm(forms.ModelForm):
    url_imagem = forms.ImageField(
        label='Nova Imagem',
        widget=forms.FileInput(attrs={
            'class': 'form-control-file', 
            'accept': 'image/*'
        })
    )

    class Meta:
        model = ImagemProduto
        fields = ['url_imagem', 'ordem']
        widgets = {
            'ordem': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '1', 
                'placeholder': 'Ordem da imagem (opcional)'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ordem'].required = False
        self.fields['ordem'].help_text = 'Deixe em branco para adicionar ao final'
        

class MarcaRegistroForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nome', 'descricao', 'logo', 'status']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'logo': forms.FileInput(attrs={'class': 'form-control-file'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in ['status']:
                field.widget.attrs['class'] = 'form-check-input'

class CategoriaRegistroForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao', 'categoria_pai', 'imagem', 'status']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'imagem': forms.FileInput(attrs={'class': 'form-control-file'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude the current category from its own parent options to prevent circular references
        if self.instance.pk:
            self.fields['categoria_pai'].queryset = Categoria.objects.exclude(pk=self.instance.pk)
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in ['status']:
                field.widget.attrs['class'] = 'form-check-input'
                


class MovimentoEstoqueForm(forms.ModelForm):
    class Meta:
        model = MovimentoEstoque
        fields = ['quantidade', 'tipo', 'observacao']
        widgets = {
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '1',
                'placeholder': 'Quantidade'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observacao': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Descrição opcional do movimento'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantidade'].required = True
        self.fields['tipo'].required = True
        self.fields['observacao'].required = False