from django.shortcuts import redirect, render
from django.views.generic.edit import FormView
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.http import Http404, HttpResponse
from .forms import FormTipoEquipo
from main.constantes import FUNCIONALIDAD, FUNCION_AVERIAS


def index(request):
    request.session.set_expiry(28800)
    return redirect('/accounts/login/')


class MiPasswordChangeView(PasswordChangeView):
    template_name = "main/cambiar_password.html"
    success_url = reverse_lazy("password_change_done")


def password_change_done(request):
    return render(request, "main/cambiar_password_hecho.html")


class TipoEquipo(FormView):
    form_class = FormTipoEquipo
    template_name = "main/formulario.html"
    
    def dispatch(self, request, funcionalidad, *args, **kwargs):
        if funcionalidad not in [f.value for f in FUNCIONALIDAD]:
            raise Http404
        self.funcionalidad = funcionalidad
        return super().dispatch(request, *args, **kwargs)
        
    def post(self, request):
        if self.funcionalidad not in [f.value for f in FUNCIONALIDAD]:
            raise Http404
        if 'tipo' not in request.POST:
            return HttpResponse("No se ha encontrado el tipo de equipo en la solicitud")
        tipo_equipo = request.POST.get('tipo')
        if self.funcionalidad == FUNCIONALIDAD.CONSULTAR_AVERIA.value:
            return redirect("listar-averias", funcion=FUNCION_AVERIAS.VISUALIZAR.value, tipo_equipo=tipo_equipo)
        elif self.funcionalidad == FUNCIONALIDAD.NUEVA_AVERIA.value:
            return redirect("registrar-averia", tipo_equipo=tipo_equipo)
        elif self.funcionalidad == FUNCIONALIDAD.MODIFICAR_AVERIA.value:
            return redirect("listar-averias", funcion=FUNCION_AVERIAS.EDITAR.value, tipo_equipo=tipo_equipo)
