from django.urls import path
from . import views
from main.views import TipoEquipo

urlpatterns = [
    path('', views.index),
    path('tipo-equipo/<int:funcionalidad>/',
         TipoEquipo.as_view(),
         name="tipo-equipo"),
]