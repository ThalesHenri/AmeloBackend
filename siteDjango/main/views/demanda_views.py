from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models import Demanda,HistoricoAtualizacao
from ..serializers import DemandaSerializer,DemandaCreateUpdateSerializer,HistoricoAtualizacaoSerializer
from ..services import DemandaService
from ..permissions import IsSupervisorOrGestor


class DemandaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSupervisorOrGestor]
    
    def get_queryset(self):
        this_user = self.request.user
        queryset = Demanda.objects.select_related(
            'condominio','profissional_acionado','criado_por'
        ).prefetch_related('anexos','historicos__usuario')
        
        if this_user.role == 'SUPERVISOR':
            return queryset.filter(condominio__supervisores__usuario=this_user)
        return queryset.filter(condominio__usuario=this_user)
    
    def get_serializer_class(self):
        if self.action in ['create','update','partial_update']:
            return DemandaCreateUpdateSerializer
        return DemandaSerializer
    
    
    @action(detail=True, methods=['get'], url_path='historico')
    def historico(self, request, pk=None):
        demanda = self.get_object()
        historicos = HistoricoAtualizacao.objects.filter(demanda=demanda).select_related('usuario')
        serializer = HistoricoAtualizacaoSerializer(historicos, many=True)
        return Response(serializer.data)
    
    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        this_dados_validados = serializer.validated_data
        demanda = DemandaService.criar_demanda(
            request.user,this_dados_validados
            
        )
        
        response_serializer = DemandaSerializer(demanda)
        return Response(response_serializer.data,status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        demanda = self.get_object()
        serializer = self.get_serializer(demanda, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        demanda_atualizada = DemandaService.atualizar_demanda(
            request.user, demanda, serializer.validated_data
        )
        
        response_serializer = DemandaSerializer(demanda_atualizada)
        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        demanda = self.get_object()
        DemandaService.deletar_demanda(request.user, demanda)
        return Response(status=status.HTTP_204_NO_CONTENT)