from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from ..models import Supervisor, Usuario

SENHA_PADRAO = "123456"

class SupervisorService:
    @staticmethod
    @transaction.atomic
    def criar_supervisor(user, dados_validados):
        """Cria o perfil do supervisor e valida a carteira de condomínios alocados."""
        if user.role != 'GESTOR':
            raise PermissionDenied("Apenas Gestores podem gerenciar perfis de supervisores.")

        condominios = dados_validados.pop('condominios', [])

        for condo in condominios:
            if condo.usuario != user:
                raise PermissionDenied(f"O condomínio '{condo.nome}' não faz parte da sua gestão.")

        # Extrai o dict de usuario e cria a instância real ANTES do Supervisor
        usuario_data = dados_validados.pop('usuario')
        if not usuario_data.get('password'):
            usuario_data['password'] = SENHA_PADRAO
        novo_usuario = Usuario.objects.create_user(**usuario_data)
        novo_usuario.role = 'SUPERVISOR'    
        novo_usuario.save()

        supervisor = Supervisor.objects.create(
            gestor=user, usuario=novo_usuario, **dados_validados
        )

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
        ativo = dados_novos.pop('ativo', None)
        if condominios is not None:
            for condo in condominios:
                if condo.usuario != this_usuario:
                    raise PermissionDenied(f"O condomínio '{condo.nome}' não pertence à sua carteira de condominios.")

        # Se vier dados de 'usuario' aninhado, atualiza os campos do Usuario relacionado
        usuario_data = dados_novos.pop('usuario', None)
        if usuario_data:
            usuario_instance = supervisor.usuario
            for campo, valor in usuario_data.items():
                if campo == 'password':
                    usuario_instance.set_password(valor)
                else:
                    setattr(usuario_instance, campo, valor)
            usuario_instance.save()

        if ativo is not None:
            supervisor.usuario.is_active = ativo
            supervisor.usuario.save(update_fields=['is_active'])

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