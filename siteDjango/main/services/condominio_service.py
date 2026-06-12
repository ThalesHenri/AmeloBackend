from rest_framework.exceptions import PermissionDenied
from ..models import Condominio, Supervisor, Usuario


class CondominioService:
    
    @staticmethod
    def criar_condominio(dados_validados: dict, this_usuario: Usuario):
        # Cadastra um condomínio e associa o ao gestor logado
        print(f"DEBUG: Tipo do usuário recebido: {type(this_usuario)}")
        print(f"DEBUG: Valor do usuário: {this_usuario}")
        if this_usuario.role != 'GESTOR':
            raise PermissionDenied("Apenas gestores podem criar condomínios.")
        
        condominio = Condominio.objects.create(
            usuario=this_usuario,
            **dados_validados
        )
        
        return condominio
    
    @staticmethod
    def atualizar_condominio(this_usuario: Usuario, condominio: Condominio, dados_validados: dict):
        # Atualiza os dados se o usuário for gestor ligado a ele
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