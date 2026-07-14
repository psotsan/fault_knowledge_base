from django.urls import path
from . import views
from main.views import TipoEquipo, MiPasswordChangeView

urlpatterns = [
    path('', views.index),
    path('tipo-equipo/<int:funcionalidad>/',
         TipoEquipo.as_view(),
         name="tipo-equipo"),
    path('cambiar-password/',
         MiPasswordChangeView.as_view(),
         name="cambiar-password"),
    path('cambiar-password/hecho/',
         views.password_change_done,
         name="cambiar-password-hecho"),
]