from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from ..models import Anexo
from ..serializers import AnexoSerializer
from ..permissions import IsSupervisorOrGestor

class AnexoViewSet(viewsets.ModelViewSet):
    queryset = Anexo.objects.all()
    serializer_class = AnexoSerializer
    permission_classes = [IsSupervisorOrGestor]
    
    # Isso diz ao Django para receber arquivos binários, não apenas JSON"
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        # O Flutter vai mandar o 'arquivo' e a 'demanda' (ID)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)