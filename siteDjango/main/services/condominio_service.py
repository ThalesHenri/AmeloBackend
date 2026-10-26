from rest_framework.exceptions import PermissionDenied
from ..models import Condominio, Supervisor, Usuario


class CondominioService:
    
    @staticmethod
    def criar_condominio(dados_validados: dict, this_usuario: Usuario):
        supervisor = None
        gestor = this_usuario
        if this_usuario.role == 'SUPERVISOR':
            try:
                supervisor = Supervisor.objects.select_related('gestor').get(usuario=this_usuario)
            except Supervisor.DoesNotExist:
                raise PermissionDenied("Supervisor sem gestor associado.")
            gestor = supervisor.gestor
        elif this_usuario.role != 'GESTOR':
            raise PermissionDenied("Apenas gestores e supervisores podem criar condomínios.")
        
        condominio = Condominio.objects.create(
            usuario=gestor,
            **dados_validados
        )
        if supervisor:
            supervisor.condominios.add(condominio)
        
        return condominio
    
    @staticmethod
    def atualizar_condominio(this_usuario: Usuario, condominio: Condominio, dados_validados: dict):
        # Condomínios pertencem ao gestor; supervisores só podem cadastrá-los.
        if condominio.usuario != this_usuario:
            raise PermissionDenied("Você não tem permissão para atualizar este condomínio.")
        
        for campo,valor in dados_validados.items():
            setattr(condominio, campo, valor)
            
        condominio.save()
        return condominio
    
    @staticmethod
    def deletar_condominio(this_usuario: Usuario, condominio: Condominio):
        # Deleta o condomínio se o usuário for gestor ligado a ele
        if condominio.usuario != this_usuario:
            raise PermissionDenied("Você não tem permissão para deletar este condomínio.")
        if condominio.usuario.role != 'GESTOR':
            raise PermissionDenied("Apenas gestores podem deletar condomínios.")
        
        condominio.delete()  