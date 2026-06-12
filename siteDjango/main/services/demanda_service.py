from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from ..models import Demanda, HistoricoAtualizacao,Supervisor,Usuario


class DemandaService:
    
    #Criar Demanda
    @staticmethod
    @transaction.atomic
    def criar_demanda(this_usuario: Usuario, dados_validados: dict)-> Demanda:
        this_condominio = dados_validados.get('condominio')
        if this_usuario.role == "SUPERVISOR":
            if not Supervisor.objects.filter(usuario=this_usuario, condominio=this_condominio).exists():
                raise PermissionDenied("Supervisor não pertence a esse condomínio.")
        
        demanda = Demanda.objects.create(
            criado_por=this_usuario, 
            status='PENDENTE',
            **dados_validados)
        
        HistoricoAtualizacao.objects.create(
            demanda=demanda,
            usuario=this_usuario,
        
            descricao_alteracao=f"CRIAÇÃO! Demanda criada por {this_usuario.get_full_name()} ({this_usuario.get_role_display()})"
        ) 
        return demanda
        
    
    
    
    #Atualizar Demanda
    @staticmethod
    @transaction.atomic
    def atualizar_demanda(self, this_usuario: Usuario, demanda:Demanda, dados_atualizados: dict) -> Demanda:
        if this_usuario.role == 'SUPERVISOR':
            if not Supervisor.objects.filter(usuario=this_usuario, condominio=demanda.condominio).exists():
                raise PermissionDenied("Supervisor não pertence a esse condomínio.")
            
            campos_permitidos = {'status','observacoes','profissional_acionado'}
            campos_enviados = set(dados_atualizados.keys())
            if not campos_enviados.issubset(campos_permitidos):
                raise PermissionDenied("Supervisor só pode atualizar status, observações e profissional acionado.")

        historico_mudancas = []
        for campo, novo_valor in dados_atualizados.items():
            valor_antigo = getattr(demanda, campo)
            if valor_antigo != novo_valor:
                setattr(demanda, campo, novo_valor)
                if campo == 'status':
                    demanda.status = novo_valor
                    historico_mudancas.append(f"{this_usuario.get_full_name()} ({this_usuario.get_role_display()}) mudou o status de '{valor_antigo}' para '{novo_valor}'")
                elif campo == 'observacoes':
                    demanda.observacoes = novo_valor
                    historico_mudancas.append(f"{this_usuario.get_full_name()} ({this_usuario.get_role_display()}) atualizou as observações.")
                elif campo == 'profissional_acionado':
                    demanda.profissional_acionado = novo_valor
                    historico_mudancas.append(f"{this_usuario.get_full_name()} ({this_usuario.get_role_display()}) alterou o profissional acionado.")
                else:
                    setattr(demanda, campo, novo_valor)
                    historico_mudancas.append(f"{this_usuario.get_full_name()} ({this_usuario.get_role_display()}) atualizou o campo '{campo}' de '{valor_antigo}' para '{novo_valor}'")
        if historico_mudancas:
            demanda.save()
            HistoricoAtualizacao.objects.create(
                demanda=demanda,
                usuario=this_usuario,
                descricao_alteracao="; ".join(historico_mudancas)
            )
        return demanda
    #Deletar Demanda
    @staticmethod
    @transaction.atomic
    def deletar_demanda(self,this_user, demanda):
        # Somente GESTOR deleta a demanda
        if this_user.role != 'GESTOR':
            raise PermissionDenied("Apenas o gestor pode deletar uma demanda.")
        demanda.delete()
        if demanda.condominio.usuario != this_user:
            raise PermissionDenied("O gestor só pode deletar demandas do seu próprio condomínio.")
        demanda.delete()
        HistoricoAtualizacao.objects.create(
            demanda=demanda,
            usuario=this_user,
            descricao_alteracao=f"{this_user.get_full_name()} ({this_user.get_role_display()}) deletou a demanda."
        )