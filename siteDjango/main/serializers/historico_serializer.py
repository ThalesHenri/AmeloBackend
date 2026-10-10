from rest_framework import serializers
from ..models import HistoricoAtualizacao
from .usuario_serializer import UsuarioSerializer

class HistoricoAtualizacaoSerializer(serializers.ModelSerializer):
    usuarioDetalhe = UsuarioSerializer(source='usuario', read_only=True)

    class Meta:
        model = HistoricoAtualizacao
        fields = ['id', 'demanda', 'descricaoAlteracao', 'dataRegistro', 'usuarioDetalhe']