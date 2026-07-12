#!/usr/bin/env python3
"""
Script para cargar datos de prueba en la base de datos.
Elimina los datos existentes y crea nuevos tipos de equipo, modelos y averías.
Cada avería recibe entre 0 y 3 referencias inventadas de forma aleatoria.

Uso:
    python cargar_datos.py
"""
import os
import sys
import random

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'averias.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from main.models import MasterEquipos, MasterModelos
from glosario_averias.models import Averia

# ──────────────────────────────────────────────
# Referencias inventadas
# ──────────────────────────────────────────────

REFERENCIAS = [
    'CAL-001', 'CAL-002', 'CAL-003',
    'MEC-001', 'MEC-002', 'MEC-003',
    'ELE-001', 'ELE-002', 'ELE-003',
    'OPT-001', 'OPT-002',
    'HID-001', 'HID-002',
    'TER-001', 'TER-002',
    'SOF-001', 'SOF-002', 'SOF-003',
    'FIR-001',
    'MAN-001', 'MAN-002',
    'SEG-001',
    'COM-001', 'COM-002',
    'ROD-001', 'ROD-002',
    'SEN-001', 'SEN-002', 'SEN-003',
    'BOM-001', 'BOM-002',
    'VAL-001', 'VAL-002',
    'PAN-001',
    'PCB-001', 'PCB-002',
]


def generar_referencias():
    """Devuelve entre 0 y 3 referencias separadas por comas"""
    cantidad = random.randint(0, 3)
    if cantidad == 0:
        return ''
    seleccionadas = random.sample(REFERENCIAS, cantidad)
    return ', '.join(seleccionadas)


# ──────────────────────────────────────────────
# Configuración
# ──────────────────────────────────────────────

TIPOS_EQUIPO = [
    {
        'nombre': 'Escáner',
        'modelos': [
            {
                'nombre': 'Midi II',
                'averias': [
                    ('Error de calibración', 'Las imágenes digitalizadas presentan distorsión geométrica', 'Ejecutar calibración con la plantilla patrón y verificar rodillos'),
                    ('Fallo en el alimentador', 'El documento no avanza o se atasca al inicio', 'Limpiar rodillos de alimentación y comprobar el sensor de papel'),
                    ('Rayas en la imagen', 'Aparecen líneas verticales en la digitalización', 'Limpiar la barra de contacto CIS con alcohol isopropílico'),
                    ('Error de comunicación USB', 'El equipo no es detectado por el ordenador', 'Reemplazar el cable USB y reinstalar el controlador'),
                    ('Ruido excesivo al escanear', 'El motor del carro emite un sonido anómalo', 'Lubricar el riel guía del carro y revisar la correa de transmisión'),
                    ('Imagen demasiado oscura', 'La digitalización sale con baja luminosidad', 'Ajustar los parámetros de exposición en el software'),
                    ('Fallo en el sensor de documentos', 'No detecta la presencia de papel', 'Limpiar el sensor óptico con aire comprimido'),
                    ('Error de temperatura', 'El equipo se apaga tras unos minutos de uso', 'Revisar el ventilador interno y limpiar las rejillas de ventilación'),
                ],
            },
            {
                'nombre': 'P250',
                'averias': [
                    ('Error de calibración', 'Las imágenes presentan franjas de color desiguales', 'Realizar calibración de blancos y negros con la hoja de referencia'),
                    ('Fallo en rodillo separador', 'Varias hojas pasan a la vez', 'Limpiar o reemplazar el rodillo separador de goma'),
                    ('Manchas en la imagen', 'Aparecen puntos negros recurrentes en la digitalización', 'Limpiar el cristal del escáner y los espejos internos'),
                    ('Error de conexión de red', 'No se puede enviar la digitalización a la carpeta de red', 'Verificar la configuración IP y el cable de red'),
                    ('Atasco de papel frecuente', 'El documento se detiene a mitad del recorrido', 'Revisar y limpiar los rodillos de arrastre internos'),
                    ('Imagen con bandas', 'Aparecen franjas horizontales en la imagen', 'Revisar la estabilidad de la fuente de luz LED'),
                    ('Fallo en el panel de control', 'Los botones del panel no responden', 'Reiniciar el equipo y verificar el cable plano del panel'),
                    ('Error de memoria insuficiente', 'No completa digitalizaciones de gran tamaño', 'Reducir la resolución de escaneado o ampliar la memoria'),
                ],
            },
            {
                'nombre': 'P1000',
                'averias': [
                    ('Error de calibración', 'La escala de grises no es uniforme', 'Ejecutar calibración completa del sensor y verificar la lámpara'),
                    ('Fallo en el duplexador', 'No digitaliza el reverso de los documentos', 'Limpiar los rodillos del duplexador y verificar el sensor de inversión'),
                    ('Imagen desplazada', 'La digitalización aparece cortada o descentrada', 'Ajustar los márgenes de detección en el software de configuración'),
                    ('Error de firmware', 'El equipo se reinicia cíclicamente', 'Actualizar el firmware a la versión más reciente'),
                    ('Baja velocidad de escaneo', 'El rendimiento es muy inferior al esperado', 'Reducir la resolución y verificar que no haya procesos en segundo plano'),
                    ('Fallo en la fuente de alimentación', 'El equipo no enciende', 'Reemplazar la fuente de alimentación interna'),
                    ('Problema de enfoque', 'Las imágenes aparecen borrosas', 'Limpiar la lente del sistema óptico y reajustar el enfoque'),
                    ('Error del sensor de profundidad', 'No detecta correctamente el grosor del original', 'Calibrar el sensor de profundidad con la plantilla de referencia'),
                ],
            },
            {
                'nombre': 'P480',
                'averias': [
                    ('Error de calibración', 'Los colores de la imagen no son fieles al original', 'Realizar perfilado ICC con la carta de color patrón'),
                    ('Fallo en el transporte', 'El documento se detiene a mitad del recorrido', 'Limpiar la banda transportadora y verificar la tensión'),
                    ('Imagen con ruido digital', 'Aparecen píxels aleatorios en la digitalización', 'Reducir la ganancia del sensor y comprobar la temperatura'),
                    ('Error de software', 'La aplicación de escaneo se cierra inesperadamente', 'Reinstalar el software y los controladores del equipo'),
                    ('Sobrecalentamiento', 'El equipo se calienta en exceso durante uso continuado', 'Limpiar los filtros de aire y verificar los ventiladores'),
                    ('Fallo en el escáner de códigos', 'No lee los códigos de barras de las láminas', 'Limpiar el lector de códigos y verificar la iluminación'),
                    ('Error de alimentación dual', 'No cambia entre los dos modos de alimentación', 'Revisar el relé de conmutación de la fuente'),
                    ('Desgaste en rodillos', 'Los documentos salen con marcas de arrastre', 'Reemplazar el juego de rodillos de arrastre'),
                ],
            },
        ],
    },
    {
        'nombre': 'Procesador de tejidos',
        'modelos': [
            {
                'nombre': 'Excelsior AS',
                'averias': [
                    ('Error de temperatura en estufa', 'La parafina no se mantiene a la temperatura correcta', 'Revisar la resistencia calefactora y el termostato'),
                    ('Fallo en la bomba de reactivos', 'No dosifica correctamente los reactivos', 'Limpiar la bomba peristáltica y reemplazar los tubos si es necesario'),
                    ('Error de nivel de parafina', 'Sensor de nivel no detecta el baño de parafina', 'Limpiar el sensor de nivel con xilol y verificar su funcionamiento'),
                    ('Programa no guarda', 'Los protocolos programados se pierden al apagar', 'Reemplazar la batería de la placa base'),
                    ('Fallo en el brazo robótico', 'El brazo no posiciona las cestas correctamente', 'Calibrar los sensores de posición del brazo'),
                    ('Error de ventilación', 'El extractor de vapores no funciona', 'Revisar el motor del extractor y limpiar los conductos'),
                    ('Fuga en el circuito de reactivos', 'Restos de líquido en la bandeja inferior', 'Revisar las conexiones y reemplazar juntas tóricas'),
                    ('Pantalla táctil sin respuesta', 'La interfaz no responde al tacto', 'Reiniciar el equipo y recalibrar la pantalla táctil'),
                ],
            },
            {
                'nombre': 'Revos',
                'averias': [
                    ('Error de temperatura en horno', 'La cera no alcanza el punto de fusión', 'Revisar el termopar y la placa de control de temperatura'),
                    ('Fallo en la válvula dosificadora', 'El caudal de reactivo no es uniforme', 'Desmontar y limpiar la válvula dosificadora'),
                    ('Error de tiempo de proceso', 'Los tiempos de los pasos no se cumplen', 'Revisar el reloj interno y sincronizar con el software'),
                    ('Fallo en el sensor de cestas', 'No detecta si hay cestas en el rotor', 'Limpiar el sensor óptico y verificar su alineación'),
                    ('Alarma de sobrepresión', 'El sistema de vacío muestra presión anómala', 'Revisar las mangueras de vacío y el filtro de seguridad'),
                    ('Error de comunicación con el host', 'No se conecta al sistema LIS', 'Verificar la configuración de red y el cable Ethernet'),
                    ('Fallo en el agitador', 'Los reactivos no se mezclan uniformemente', 'Revisar el motor del agitador y su acoplamiento'),
                    ('Corrosión en el baño de parafina', 'Aparecen partículas en la parafina fundida', 'Drenar el baño, limpiar y reemplazar la parafina'),
                ],
            },
        ],
    },
]

# ──────────────────────────────────────────────
# Función principal
# ──────────────────────────────────────────────

def main():
    random.seed(42)  # Semilla fija para que las referencias sean reproducibles

    print('Limpiando datos existentes...')
    Averia.objects.all().delete()
    MasterModelos.objects.all().delete()
    MasterEquipos.objects.all().delete()

    total_averias = 0
    total_con_ref = 0

    for tipo_data in TIPOS_EQUIPO:
        tipo_equipo = MasterEquipos.objects.create(tipo=tipo_data['nombre'])
        print(f'\nTipo de equipo creado: {tipo_equipo.tipo}')

        for modelo_data in tipo_data['modelos']:
            modelo = MasterModelos.objects.create(
                modelo=modelo_data['nombre'],
                tipo=tipo_equipo,
            )
            print(f'  Modelo: {modelo.modelo}')

            for averia_data in modelo_data['averias']:
                refs = generar_referencias()
                Averia.objects.create(
                    modelo=modelo,
                    averia=averia_data[0],
                    sintoma=averia_data[1],
                    solucion=averia_data[2],
                    ref=refs,
                    ult_edic='admin',
                )
                total_averias += 1
                if refs:
                    total_con_ref += 1

            print(f'    Averías creadas: {len(modelo_data["averias"])}')

    print(f'\n─── Resumen ───')
    print(f'Tipos de equipo: {len(TIPOS_EQUIPO)}')
    print(f'Modelos: {MasterModelos.objects.count()}')
    print(f'Averías: {total_averias}')
    print(f'  - Con referencias: {total_con_ref}')
    print(f'  - Sin referencias: {total_averias - total_con_ref}')
    print('Datos cargados correctamente')


if __name__ == '__main__':
    main()
