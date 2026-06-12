from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models import Supervisor
from ..serializers import SupervisorSerializer
from ..services import SupervisorService
from ..permissions import IsGestorOnly

class SupervisorViewSet(viewsets.ModelViewSet):
    serializer_class = SupervisorSerializer
    permission_classes = [IsGestorOnly]

    def get_queryset(self):
        # Traz os condomínios aninhados para otimizar o GET
        return Supervisor.objects.filter(gestor=self.request.user).prefetch_related('condominios')

    def create(self, request, *args, **kwargs):
        #valida os dados
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        #chama o service
        supervisor = SupervisorService.criar_supervisor(request.user, serializer.validated_data)
        
        response_serializer = SupervisorSerializer(supervisor)
        #retorna o status 201
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        supervisor = self.get_object()
        serializer = self.get_serializer(supervisor, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        supervisor_atualizado = SupervisorService.atualizar_supervisor(
            request.user, supervisor, serializer.validated_data
        )
        
        response_serializer = SupervisorSerializer(supervisor_atualizado)
        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        supervisor = self.get_object()
        SupervisorService.deletar_supervisor(request.user, supervisor)
        return Response(status=status.HTTP_204_NO_CONTENT)