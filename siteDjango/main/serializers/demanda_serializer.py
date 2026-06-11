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
    profissional_acionado = ProfissionalSerializer(read_only=True)
    criado_por = UsuarioSerializer(read_only=True)
    anexos = AnexoSerializer(many=True, read_only=True)
    # Puxa o relacionados usando o related_name='historicos' definido no Model
    historicos = HistoricoAtualizacaoSerializer(many=True, read_only=True)

    class Meta:
        model = Demanda
        fields = [
            'id', 'titulo', 'descricao', 'urgencia', 'status', 
            'data_abertura', 'previsao_conclusao', 'observacoes',
            'condominio', 'profissional_acionado', 'criado_por', 
            'anexos', 'historicos'
        ]

# SERIALIZER DE ESCRITA (POST/PUT/PATCH) - Aceita chaves primárias (IDs)
class DemandaCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Demanda
        fields = [
            'id', 'condominio', 'titulo', 'descricao', 
            'urgencia', 'profissional_acionado', 'status', 
            'previsao_conclusao', 'observacoes'
        ]
        read_only_fields = ['criado_por', 'status']