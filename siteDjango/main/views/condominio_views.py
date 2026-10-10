from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models import Condominio
from ..serializers import CondominioSerializer
from ..services import CondominioService
from ..permissions import IsSupervisorOrGestor
#trocar para isGestor na segunda versão

class CondominioViewSet(viewsets.ModelViewSet):
    serializer_class = CondominioSerializer
    permission_classes = [IsSupervisorOrGestor]

    def get_queryset(self):
        this_user = self.request.user
        if this_user.role == 'SUPERVISOR':
            return Condominio.objects.filter(supervisores__usuario=this_user)
        return Condominio.objects.filter(usuario=this_user)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        condominio = CondominioService.criar_condominio(serializer.validated_data,request.user)
        
        response_serializer = CondominioSerializer(condominio)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        condominio = self.get_object()
        serializer = self.get_serializer(condominio, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        condominio_atualizado = CondominioService.atualizar_condominio(
            request.user, condominio, serializer.validated_data
        )
        
        response_serializer = CondominioSerializer(condominio_atualizado)
        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        condominio = self.get_object()
        CondominioService.deletar_condominio(request.user, condominio)
        return Response(status=status.HTTP_204_NO_CONTENT)