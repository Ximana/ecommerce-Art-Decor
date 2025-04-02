from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from apps.usuarios.models import Usuario

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


