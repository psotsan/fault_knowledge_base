from django.db import models
from main.models import MasterModelos

class Averia(models.Model):
    modelo = models.ForeignKey(
        MasterModelos, 
        on_delete=models.CASCADE,
        to_field='id'
    )

    averia = models.CharField(
        max_length=100,
        help_text="Descripción de la avería"
    )

    sintoma = models.CharField(
        max_length=100,
        help_text="Síntomas de la avería"
    )

    solucion = models.CharField(
        max_length=100,
        help_text="Solución a la avería"
    )

    ref = models.CharField(
        max_length=150,
        help_text="Referencias asociadas a la avería, separadas por comas",
        blank=True
    )

    ult_edic = models.CharField(
        max_length=15,
        help_text="Usuario de la última edición"
    )

    ult_fecha = models.DateField(
        auto_now=True,
        help_text="Fecha de la última edición"
    )

    def __str__(self):
        return f"{self.modelo} - {self.averia}"

