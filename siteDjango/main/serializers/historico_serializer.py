from rest_framework import serializers
from ..models import HistoricoAtualizacao
from .usuario_serializer import UsuarioSerializer

class HistoricoAtualizacaoSerializer(serializers.ModelSerializer):
    usuario_detalhe = UsuarioSerializer(source='usuario', read_only=True)

    class Meta:
        model = HistoricoAtualizacao
        fields = ['id', 'demanda', 'descricao_alteracao', 'data_registro', 'usuario_detalhe']