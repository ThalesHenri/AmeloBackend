from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Demanda
from ..serializers import UsuarioSerializer
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
        if request.user.role == 'SUPERVISOR':
            queryset = Demanda.objects.filter(condominio__supervisores__usuario=request.user)
        else:
            queryset = Demanda.objects.filter(condominio__usuario=request.user)

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