"""
URL configuration for averias project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("main.urls")),
    path('glosario_averias/', include("glosario_averias.urls")),
    path('accounts/', include('django.contrib.auth.urls')),
]

