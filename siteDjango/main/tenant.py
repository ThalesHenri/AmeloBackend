from rest_framework.exceptions import PermissionDenied

from .models import Supervisor


def gestor_id_do_usuario(usuario):
    """Retorna o gestor que delimita os dados visíveis ao usuário."""
    if usuario.role == 'GESTOR':
        return usuario.id
    if usuario.role == 'SUPERVISOR':
        gestor_id = Supervisor.objects.filter(usuario=usuario).values_list(
            'gestor_id', flat=True
        ).first()
        if gestor_id is not None:
            return gestor_id
        raise PermissionDenied("Supervisor sem gestor associado.")
    raise PermissionDenied("Usuário sem gestor responsável.")