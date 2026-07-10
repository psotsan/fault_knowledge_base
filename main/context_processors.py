import json
from pathlib import Path


def tema(request):
    """Carga la configuración del tema desde tema.json y la pone a
    disposición de todas las plantillas."""
    ruta_tema = Path(__file__).resolve().parent / 'tema.json'
    with open(ruta_tema, encoding='utf-8') as f:
        config = json.load(f)
    return {'tema': config}
