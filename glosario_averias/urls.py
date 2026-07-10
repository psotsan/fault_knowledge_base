from django.urls import path
from . import views, forms
from django.contrib.auth.decorators import login_required

urlpatterns = [
     path('registrar-averia/<int:tipo_equipo>/',
         login_required(views.RegistrarAveria.as_view()),
         name='registrar-averia'),
     path('listar-averias/<int:funcion>/<int:tipo_equipo>/',
         login_required(views.ListarAverias.as_view()),
         name='listar-averias'),
     path('consultar-averias/<int:tipo_equipo>/<int:pk>/',
         login_required(views.DetalleAveria.as_view()),
         name='detalle-averia'),
     path('editar-averia/<int:tipo_equipo>/<int:pk>/',
         login_required(views.EditarAveria.as_view()),
         name='editar-averia',
    )
]