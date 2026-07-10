from django import forms
from main.models import MasterModelos
from main.funciones import get_modelos_por_tipo
from .models import Averia


def get_form_filtro(tipo_equipo):
    """Genera dinámicamente un formulario de filtro para el listado de averías"""
    qs = get_modelos_por_tipo(tipo_equipo)

    form_filtro = forms.modelform_factory(
        Averia,
        fields=['modelo', 'averia', 'sintoma', 'solucion'],
        widgets={
            "modelo": forms.Select(
                attrs={
                    'placeholder': "Modelo",
                    'class': 'form-select form-control'
                }),
            "averia": forms.TextInput(attrs={
                'placeholder': "Avería",
                'class': 'form-control'
            }),
            "sintoma": forms.TextInput(attrs={
                'placeholder': "Síntomas",
                'class': 'form-control'
            }),
            "solucion": forms.TextInput(attrs={
                'placeholder': "Solución",
                'class': 'form-control'
            })
        })

    form_filtro.base_fields['modelo'].required = False
    form_filtro.base_fields['averia'].required = False
    form_filtro.base_fields['sintoma'].required = False
    form_filtro.base_fields['solucion'].required = False
    form_filtro.base_fields['modelo'].queryset = qs
    return form_filtro


class FormularioAveria(forms.ModelForm):
    """Formulario compartido para crear y editar averías"""
    class Meta:
        model = Averia
        fields = ['modelo', 'averia', 'sintoma', 'solucion', 'ref']
        widgets = {
            "modelo": forms.Select(attrs={
                'placeholder': "Modelo",
                'class': 'form-select form-control'
            }),
            "averia": forms.TextInput(attrs={
                'placeholder': "Avería",
                'class': 'form-control'
            }),
            "sintoma": forms.Textarea(attrs={
                'placeholder': "Síntomas",
                'class': 'form-control',
                'style': 'min-height: 100px'
            }),
            "solucion": forms.Textarea(attrs={
                'placeholder': "Solución",
                'class': 'form-control',
                'style': 'min-height: 100px'
            }),
            "ref": forms.Textarea(attrs={
                'placeholder': "Referencias",
                'class': 'form-control',
                'style': 'min-height: 100px'
            }),
        }

    def __init__(self, *args, **kwargs):
        tipo_equipo = kwargs.pop('tipo_equipo', None)
        super().__init__(*args, **kwargs)
        if tipo_equipo:
            self.fields['modelo'].queryset = get_modelos_por_tipo(tipo_equipo)


def get_form_registrar_averia(tipo_equipo):
    """Devuelve la clase FormularioAveria configurada con el tipo de equipo"""
    qs = get_modelos_por_tipo(tipo_equipo)

    form = forms.modelform_factory(
        Averia,
        form=FormularioAveria,
        fields=['modelo', 'averia', 'sintoma', 'solucion', 'ref'],
    )

    form.base_fields['modelo'].queryset = qs
    return form
