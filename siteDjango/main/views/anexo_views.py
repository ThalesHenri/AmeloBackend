from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from ..models import Anexo
from ..serializers import AnexoSerializer
from ..permissions import IsSupervisorOrGestor
from ..tenant import gestor_id_do_usuario
from rest_framework.exceptions import PermissionDenied

class AnexoViewSet(viewsets.ModelViewSet):
    serializer_class = AnexoSerializer
    permission_classes = [IsSupervisorOrGestor]
    
    # Isso diz ao Django para receber arquivos binários, não apenas JSON"
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return Anexo.objects.filter(
            demanda__condominio__usuario_id=gestor_id_do_usuario(self.request.user)
        )

    def create(self, request, *args, **kwargs):
        # O Flutter vai mandar o 'arquivo' e a 'demanda' (ID)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        demanda = serializer.validated_data.get('demanda')
        if demanda and demanda.condominio.usuario_id != gestor_id_do_usuario(request.user):
            raise PermissionDenied("Você não pode anexar arquivos a demandas de outro gestor.")
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)