from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models import Profissional
from ..serializers import ProfissionalSerializer
from ..services import ProfissionalService
from ..permissions import IsGestorOnly

class ProfissionalViewSet(viewsets.ModelViewSet):
    serializer_class = ProfissionalSerializer
    permission_classes = [IsGestorOnly]

    def get_queryset(self):
        return Profissional.objects.filter(usuario=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profissional = ProfissionalService.criar_profissional(request.user, serializer.validated_data)
        response_serializer = ProfissionalSerializer(profissional)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        profissional = self.get_object()
        serializer = self.get_serializer(profissional, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        profissional_atualizado = ProfissionalService.atualizar_profissional(
            request.user, profissional, serializer.validated_data
        )
        response_serializer = ProfissionalSerializer(profissional_atualizado)
        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        profissional = self.get_object()
        ProfissionalService.deletar_profissional(request.user, profissional)
        return Response(status=status.HTTP_204_NO_CONTENT)