from rest_framework.exceptions import PermissionDenied
from ..models import Profissional, Supervisor


def _gestor_responsavel(usuario):
    if usuario.role == 'GESTOR':
        return usuario
    if usuario.role == 'SUPERVISOR':
        try:
            return Supervisor.objects.only('gestor_id').get(usuario=usuario).gestor
        except Supervisor.DoesNotExist:
            raise PermissionDenied("Supervisor sem gestor associado.")
    raise PermissionDenied("Apenas gestores e supervisores podem gerenciar profissionais.")

class ProfissionalService:
    
    @staticmethod
    def criar_profissional(this_usuario, dados_validados):
        gestor = _gestor_responsavel(this_usuario)
        return Profissional.objects.create(usuario=gestor, **dados_validados)

    @staticmethod
    def atualizar_profissional(this_usuario, profissional, dados_novos):
        if profissional.usuario != _gestor_responsavel(this_usuario):
            raise PermissionDenied("Este profissional não está cadastrado na base do seu gestor.")
            
        for campo, valor in dados_novos.items():
            setattr(profissional, campo, valor)
            
        profissional.save()
        return profissional

    @staticmethod
    def deletar_profissional(this_usuario, profissional):
        if profissional.usuario != _gestor_responsavel(this_usuario):
            raise PermissionDenied("Você não tem autorização para excluir este profissional.")
        profissional.delete()