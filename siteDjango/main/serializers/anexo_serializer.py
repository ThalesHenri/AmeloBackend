from rest_framework import serializers
from ..models import Anexo

class AnexoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexo
        fields = ['id', 'demanda', 'historico', 'arquivo', 'dataCriacao']