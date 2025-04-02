#/app/usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, Endereco

class UsuarioRegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario', 
                 'telefone', 'bi', 'data_nascimento', 
                 'foto_perfil', 'password1', 'password2')
        widgets = {
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control-file'}),
            'funcao': forms.Select(attrs={'class': 'form-select'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar classes Bootstrap aos campos
        for field_name, field in self.fields.items():
            if field_name == 'tipo_usuario':
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'
                

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['tipo', 'provincia', 'municipio', 'distrito', 'bairro', 'rua', 'casa', 'principal']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'distrito': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'casa': forms.TextInput(attrs={'class': 'form-control'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
