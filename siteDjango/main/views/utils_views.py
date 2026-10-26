from django.http import JsonResponse
from ..models import HistoricoAtualizacao 
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from ..models import Demanda
from ..models import Profissional, Supervisor
from ..tenant import gestor_id_do_usuario
from ..serializers import UsuarioSerializer, RedefinirSenhaSerializer
from ..services import HealthService

class HealthCheckView(View):
    def get(self, request, *args, **kwargs):
        health_data = HealthService.check_system_health()
        
        status_code = 200 if health_data["is_healthy"] else 503
        return JsonResponse(health_data["data"], status=status_code)

class AuthMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data, status=200)

class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Demanda.objects.filter(
            condominio__usuario_id=gestor_id_do_usuario(request.user)
        )

        total = queryset.count()
        abertas = queryset.filter(status='PENDENTE').count()
        andamento = queryset.filter(status='EM_ANDAMENTO').count()
        concluidas = queryset.filter(status='CONCLUIDA').count()
        urgentes = queryset.filter(urgencia='URGENTE').count()

        return Response({
            'total': total,
            'abertas': abertas,
            'em_andamento': andamento,
            'concluidas': concluidas,
            'urgentes': urgentes,
        }, status=200)


class AtividadesSupervisoresView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        #validação de role do usuário
        if request.user.role != 'GESTOR':
            return Response({'detail': 'Apenas Gestores podem ver este recurso.'}, status=403)

        historicos = HistoricoAtualizacao.objects.filter(
            usuario__role='SUPERVISOR',
            demanda__condominio__usuario=request.user
        ).select_related('usuario', 'demanda').order_by('-dataRegistro')[:15]

        dados = [
            {
                'id': h.id,
                'descricao': h.descricaoAlteracao,
                'data': h.dataRegistro,
                'supervisor': h.usuario.get_full_name() or h.usuario.username if h.usuario else 'Supervisor removido',
                'demanda': h.demanda.titulo,
                'demandaId': h.demanda.id,
            }
            for h in historicos
        ]

        return Response(dados, status=200)


class MetricasProfissionaisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        usuario = request.user
        if usuario.role == 'SUPERVISOR':
            try:
                gestor = Supervisor.objects.only('gestor_id').get(usuario=usuario).gestor
            except Supervisor.DoesNotExist:
                return Response({'detail': 'Supervisor sem gestor associado.'}, status=403)
        elif usuario.role == 'GESTOR':
            gestor = usuario
        else:
            return Response({'detail': 'Apenas gestores e supervisores podem consultar esta métrica.'}, status=403)

        profissionais = Profissional.objects.filter(usuario=gestor).annotate(
            demandas_concluidas=Count(
                'demanda',
                filter=Q(
                    demanda__status='CONCLUIDA',
                    demanda__condominio__usuario=gestor,
                ),
            )
        ).order_by('nome', 'id')

        return Response([
            {
                'id': profissional.id,
                'nome': profissional.nome,
                'especialidade': profissional.especialidade,
                'demandas_concluidas': profissional.demandas_concluidas,
            }
            for profissional in profissionais
        ], status=200)


class RedefinirSenhaView(APIView):
    """Permite que o usuário autenticado redefina sua própria senha."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = RedefinirSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = request.user
        senha_atual = serializer.validated_data['senha_atual']
        nova_senha = serializer.validated_data['nova_senha']

        if not usuario.check_password(senha_atual):
            return Response(
                {'senha_atual': 'Senha atual incorreta.'},
                status=400,
            )

        usuario.set_password(nova_senha)
        usuario.senha_redefinida = True
        usuario.save(update_fields=['password', 'senha_redefinida'])

        return Response(
            {'detail': 'Senha redefinida com sucesso.'},
            status=200,
        )