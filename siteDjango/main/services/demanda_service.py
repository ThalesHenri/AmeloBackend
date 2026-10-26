from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from ..models import Demanda, HistoricoAtualizacao, Supervisor, Usuario
from ..tenant import gestor_id_do_usuario


def _validar_condominio_do_gestor(usuario, condominio):
    if condominio.usuario_id != gestor_id_do_usuario(usuario):
        raise PermissionDenied("O condomínio não pertence ao gestor responsável.")


def _validar_profissional_do_gestor(usuario, dados):
    profissional = dados.get('profissionalAcionado')
    if profissional is None:
        return

    gestor_id = usuario.id
    if usuario.role == 'SUPERVISOR':
        try:
            gestor_id = Supervisor.objects.only('gestor_id').get(usuario=usuario).gestor_id
        except Supervisor.DoesNotExist:
            raise PermissionDenied("Supervisor sem gestor associado.")

    if profissional.usuario_id != gestor_id:
        raise PermissionDenied("O profissional selecionado não pertence à base do gestor responsável.")


class DemandaService:

    # Criar Demanda
    @staticmethod
    @transaction.atomic
    def criar_demanda(this_usuario: Usuario, dados_validados: dict) -> Demanda:
        _validar_condominio_do_gestor(this_usuario, dados_validados['condominio'])
        _validar_profissional_do_gestor(this_usuario, dados_validados)
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
        _validar_condominio_do_gestor(this_usuario, demanda.condominio)
        if 'condominio' in dados_atualizados:
            _validar_condominio_do_gestor(this_usuario, dados_atualizados['condominio'])
        _validar_profissional_do_gestor(this_usuario, dados_atualizados)
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
        _validar_condominio_do_gestor(this_user, demanda.condominio)
        if this_user.role == 'GESTOR' and demanda.condominio.usuario != this_user:
            raise PermissionDenied("O gestor só pode deletar demandas do seu próprio condomínio.")
        if this_user.role not in {'GESTOR', 'SUPERVISOR'}:
            raise PermissionDenied("Apenas gestores e supervisores podem deletar demandas.")

        HistoricoAtualizacao.objects.create(
            demanda=demanda,
            usuario=this_user,
            descricaoAlteracao=f"{this_user.get_full_name()} ({this_user.get_role_display()}) deletou a demanda."
        )
        demanda.delete()