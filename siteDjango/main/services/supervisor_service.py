from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from ..models import Supervisor

class SupervisorService:
    
    @staticmethod
    @transaction.atomic
    def criar_supervisor(user, dados_validados):
        """Cria o perfil do supervisor e valida a carteira de condomínios alocados."""
        if user.role != 'GESTOR':
            raise PermissionDenied("Apenas Gestores podem gerenciar perfis de supervisores.")
            
        # Remove temporariamente a lista de condomínios (ManyToMany) para criar a instância primeiro
        condominios = dados_validados.pop('condominios', [])
        
       # O gestor só pode colocar o supervisor em condomínios QUE SÃO DELE
        for condo in condominios:
            if condo.usuario != user:
                raise PermissionDenied(f"O condomínio '{condo.nome}' não faz parte da sua gestão.")
                
        # Instancia o supervisor amarrando o gestor automático
        supervisor = Supervisor.objects.create(gestor=user, **dados_validados)
        
        # Sendo ManyToMany, após salvar o objeto pai, injetamos a lista de condomínios
        if condominios:
            supervisor.condominios.set(condominios)
            
        return supervisor

    @staticmethod
    @transaction.atomic
    def atualizar_supervisor(this_usuario, supervisor, dados_novos):
        """Atualiza os dados e a alocação de condomínios do supervisor."""
        if supervisor.gestor != this_usuario:
            raise PermissionDenied("Você não tem autorização para gerenciar este supervisor.")
            
        condominios = dados_novos.pop('condominios', None)
        
        # Se o Gestor estiver mudando os condomínios do supervisor, valida novamente a posse
        if condominios is not None:
            for condo in condominios:
                if condo.usuario != this_usuario:
                    raise PermissionDenied(f"O condomínio '{condo.nome}' não pertence à sua carteira de condominios.")
                    
        for campo, valor in dados_novos.items():
            setattr(supervisor, campo, valor)
        supervisor.save()
        
        if condominios is not None:
            supervisor.condominios.set(condominios)
            
        return supervisor

    @staticmethod
    @transaction.atomic
    def deletar_supervisor(user, supervisor):
        """Deleta o vínculo do supervisor (o usuário base continua existindo, apenas o perfil cai)."""
        if supervisor.gestor != user:
            raise PermissionDenied("Você não pode remover um supervisor que não trabalha para você.")
        supervisor.delete()