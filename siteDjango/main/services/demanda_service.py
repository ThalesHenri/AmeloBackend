from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from ..models import Demanda, HistoricoAtualizacao, Usuario


class DemandaService:

    # Criar Demanda
    @staticmethod
    @transaction.atomic
    def criar_demanda(this_usuario: Usuario, dados_validados: dict) -> Demanda:
        demanda = Demanda.objects.create(
            criadoPor=this_usuario,
            status='PENDENTE',
            **dados_validados
        )

        HistoricoAtualizacao.objects.create(
            demanda=demanda,
            usuario=this_usuario,
            descricaoAlteracao=f"CRIAÇÃO! Demanda criada por {this_usuario.get_full_name()} ({this_usuario.get_role_display()})"
        )
        return demanda

    # Atualizar Demanda
    @staticmethod
    @transaction.atomic
    def atualizar_demanda(this_usuario: Usuario, demanda: Demanda, dados_atualizados: dict) -> Demanda:
        if this_usuario.role == 'SUPERVISOR':
            campos_permitidos = {'status', 'observacoes', 'profissionalAcionado'}
            campos_enviados = set(dados_atualizados.keys())
            if not campos_enviados.issubset(campos_permitidos):
                raise PermissionDenied("Supervisor só pode atualizar status, observações e profissional acionado.")

        historico_mudancas = []
        for campo, novo_valor in dados_atualizados.items():
            valor_antigo = getattr(demanda, campo)
            if valor_antigo != novo_valor:
                setattr(demanda, campo, novo_valor)
                if campo == 'status':
                    historico_mudancas.append(
                        f"{this_usuario.get_full_name()} ({this_usuario.get_role_display()}) mudou o status de '{valor_antigo}' para '{novo_valor}'"
                    )
                    if novo_valor == 'CONCLUIDA' and valor_antigo != 'CONCLUIDA':
                        demanda.dataConclusao = timezone.now()
                elif campo == 'observacoes':
                    historico_mudancas.append(
                        f"{this_usuario.get_full_name()} ({this_usuario.get_role_display()}) atualizou as observações."
                    )
                elif campo == 'profissionalAcionado':
                    historico_mudancas.append(
                        f"{this_usuario.get_full_name()} ({this_usuario.get_role_display()}) alterou o profissional acionado."
                    )
                else:
                    historico_mudancas.append(
                        f"{this_usuario.get_full_name()} ({this_usuario.get_role_display()}) atualizou o campo '{campo}' de '{valor_antigo}' para '{novo_valor}'"
                    )

        if historico_mudancas:
            demanda.save()
            HistoricoAtualizacao.objects.create(
                demanda=demanda,
                usuario=this_usuario,
                descricaoAlteracao="; ".join(historico_mudancas)
            )
        return demanda

    # Deletar Demanda
    @staticmethod
    @transaction.atomic
    def deletar_demanda(this_user, demanda):
        # Somente GESTOR deleta a demanda
        if this_user.role != 'GESTOR':
            raise PermissionDenied("Apenas o gestor pode deletar uma demanda.")
        if demanda.condominio.usuario != this_user:
            raise PermissionDenied("O gestor só pode deletar demandas do seu próprio condomínio.")

        HistoricoAtualizacao.objects.create(
            demanda=demanda,
            usuario=this_user,
            descricaoAlteracao=f"{this_user.get_full_name()} ({this_user.get_role_display()}) deletou a demanda."
        )
        demanda.delete()