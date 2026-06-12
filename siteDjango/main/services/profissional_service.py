from rest_framework.exceptions import PermissionDenied
from ..models import Profissional

class ProfissionalService:
    
    @staticmethod
    def criar_profissional(this_usuario, dados_validados):
        if this_usuario.role != 'GESTOR':
            raise PermissionDenied("Apenas Gestores podem cadastrar profissionais na plataforma.")
        return Profissional.objects.create(usuario=this_usuario, **dados_validados)

    @staticmethod
    def atualizar_profissional(this_usuario, profissional, dados_novos):
        if profissional.usuario != this_usuario:
            raise PermissionDenied("Este profissional não está cadastrado na sua base de dados.")
            
        for campo, valor in dados_novos.items():
            setattr(profissional, campo, valor)
            
        profissional.save()
        return profissional

    @staticmethod
    def deletar_profissional(this_usuario, profissional):
        if profissional.usuario != this_usuario:
            raise PermissionDenied("Você não tem autorização para excluir este profissional.")
        profissional.delete()