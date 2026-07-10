from django import forms
from .models import MasterEquipos


class FormTipoEquipo(forms.ModelForm):
    class Meta:
        model = MasterEquipos
        fields = ['tipo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].widget = forms.Select(
            choices=[(o.pk, o.tipo) for o in MasterEquipos.objects.all()])
        self.fields['tipo'].widget.attrs = {
            "placeholder": "Tipo de equipo",
            "class": "form-select form-control col-10 col-sm-7 col-md-3 col-lg-2"
        }
        self.fields['tipo'].help_text = ""
