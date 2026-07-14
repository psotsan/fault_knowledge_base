from django.shortcuts import redirect
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from main.funciones import get_modelos_por_tipo

from .forms import get_form_registrar_averia, get_form_filtro
from .models import Averia
from main.models import MasterEquipos, MasterModelos
from main.constantes import FUNCION_AVERIAS


class RegistrarAveria(CreateView):
    template_name = 'glosario_averias/edicion.html'

    def dispatch(self, request, tipo_equipo, *args, **kwargs):
        if 'guardar' in request.POST:
            messages.add_message(request, messages.INFO, "Avería guardada")
        self.tipo_equipo = tipo_equipo
        self.model = Averia
        self.form_class = get_form_registrar_averia(tipo_equipo)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('registrar-averia', kwargs={'tipo_equipo': self.tipo_equipo})


class ListarAverias(ListView):
    template_name = 'glosario_averias/consultar_lista.html'
    context_object_name = 'averias'

    def dispatch(self, request, funcion, tipo_equipo, *args, **kwargs):
        self.request = request
        self.tipo_equipo = tipo_equipo
        self.funcion = funcion
        self.model = Averia
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Filtrar por tipo de equipo
        datos = Averia.objects.filter(modelo__tipo_id=self.tipo_equipo)

        # Búsqueda global: si se usa el campo "busqueda", busca en
        # avería, síntoma y solución a la vez
        busqueda = self.request.POST.get('busqueda', '').strip()
        if busqueda:
            palabras = busqueda.split()
            q_filtros = Q()
            for palabra in palabras:
                q_filtros &= (
                    Q(averia__icontains=palabra) |
                    Q(sintoma__icontains=palabra) |
                    Q(solucion__icontains=palabra)
                )
            datos = datos.filter(q_filtros)

        # Filtros específicos (se combinan con la búsqueda global)
        if 'modelo' in self.request.POST and self.request.POST.get('modelo') != '':
            str_modelo = MasterModelos.objects.get(pk=self.request.POST.get('modelo')).modelo
            datos = datos.filter(modelo__modelo__exact=str_modelo)

        if 'averia' in self.request.POST and self.request.POST.get('averia').strip():
            strings_averia = self.request.POST.get('averia').split()
            for s in strings_averia:
                datos = datos.filter(averia__icontains=s)

        if 'sintoma' in self.request.POST and self.request.POST.get('sintoma').strip():
            strings_sintoma = self.request.POST.get('sintoma').split()
            for s in strings_sintoma:
                datos = datos.filter(sintoma__icontains=s)

        if 'solucion' in self.request.POST and self.request.POST.get('solucion').strip():
            strings_solucion = self.request.POST.get('solucion').split()
            for s in strings_solucion:
                datos = datos.filter(solucion__icontains=s)

        # Ordenar: relevantes primero (por modelo, luego por avería)
        return datos.order_by('modelo__modelo', 'averia')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = get_form_filtro(self.tipo_equipo)
        context["visualizar"] = True if self.funcion == FUNCION_AVERIAS.VISUALIZAR.value else False
        context["tipo_equipo"] = self.tipo_equipo
        return context

    def post(self, *args, **kwargs):
        if 'filtrar' in self.request.POST:
            return self.get(self.request)
        else:
            if self.funcion == FUNCION_AVERIAS.VISUALIZAR.value:
                return redirect('detalle-averia',
                                tipo_equipo=self.tipo_equipo,
                                pk=self.request.POST.get('pk'))
            else:
                return redirect('editar-averia',
                                tipo_equipo=self.tipo_equipo,
                                pk=self.request.POST.get('pk'))


class DetalleAveria(DetailView):
    template_name = 'glosario_averias/consultar_detalle.html'

    def dispatch(self, request, tipo_equipo, *args, **kwargs):
        self.model = Averia
        return super().dispatch(request, *args, **kwargs)

class EditarAveria(UpdateView):
    template_name = 'glosario_averias/edicion.html'

    def dispatch(self, request, tipo_equipo, pk, *args, **kwargs):
        if 'guardar' in request.POST:
            messages.add_message(request, messages.INFO, "Avería guardada")
        self.tipo_equipo = tipo_equipo
        self.model = Averia
        self.form_class = get_form_registrar_averia(tipo_equipo)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        """Pasa la instancia existente y filtra el queryset de modelos por tipo de equipo."""
        form = super().get_form(form_class)
        form.fields['modelo'].queryset = get_modelos_por_tipo(self.tipo_equipo)
        return form

    def get_success_url(self):
        return reverse_lazy('listar-averias', kwargs={
            'funcion': FUNCION_AVERIAS.EDITAR.value,
            'tipo_equipo': self.tipo_equipo})

    def get_object(self, queryset=None):
        return Averia.objects.get(pk=self.kwargs['pk'])

