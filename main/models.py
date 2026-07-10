from django.db import models


class MasterEquipos(models.Model):
    """Tipos de equipo (TOC, UV, Centrífuga, etc.)"""
    tipo = models.CharField(
        max_length=50,
        help_text="Tipo de equipo"
    )
    
    def __str__(self):
        return self.tipo


class MasterModelos(models.Model):
    """Modelos concretos de equipos"""
    modelo = models.CharField(
        max_length=50,
        help_text="Modelo de equipo",
        unique=True
    )
    tipo = models.ForeignKey(
        MasterEquipos,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.modelo
