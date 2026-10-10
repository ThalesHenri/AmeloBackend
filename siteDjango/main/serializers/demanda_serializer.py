from rest_framework import serializers
from ..models import Demanda
from .condominio_serializer import CondominioSerializer
from .profissional_serializer import ProfissionalSerializer
from .usuario_serializer import UsuarioSerializer
from .anexo_serializer import AnexoSerializer
from .historico_serializer import HistoricoAtualizacaoSerializer

# SERIALIZER DE LEITURA (GET) - Entrega os dados
class DemandaSerializer(serializers.ModelSerializer):
    condominio = CondominioSerializer(read_only=True)
    profissionalAcionado = ProfissionalSerializer(read_only=True)
    criadoPor = UsuarioSerializer(read_only=True)
    anexos = AnexoSerializer(many=True, read_only=True)
    historicos = HistoricoAtualizacaoSerializer(many=True, read_only=True)

    class Meta:
        model = Demanda
        fields = [
            'id', 'titulo', 'descricao', 'urgencia', 'status',
            'dataAbertura', 'dataConclusao', 'previsaoConclusao', 'observacoes',
            'condominio', 'profissionalAcionado', 'criadoPor',
            'anexos', 'historicos'
        ]

# SERIALIZER DE ESCRITA (POST/PUT/PATCH) - Aceita chaves primárias (IDs)
class DemandaCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Demanda
        fields = [
            'id', 'condominio', 'titulo', 'descricao',
            'urgencia', 'profissionalAcionado', 'status',
            'previsaoConclusao', 'observacoes'
        ]
        read_only_fields = ['criadoPor', 'dataAbertura']

    def validate(self, attrs):
        return super().validate(attrs)
    