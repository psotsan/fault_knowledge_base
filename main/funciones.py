from .models import MasterEquipos, MasterModelos


def get_master_equipos(request, req_permiso=False):
    """Devuelve lista de tipo de equipo para selects"""
    l_equipos = [["null", "Seleccionar tipo de equipo"]]
    for e in MasterEquipos.objects.all():
        l_equipos.append([str(e.id), e.tipo])
    return l_equipos


def get_modelos_por_tipo(tipo_equipo):
    """Devuelve los modelos filtrados por tipo de equipo"""
    return MasterModelos.objects.filter(tipo_id__exact=tipo_equipo)

