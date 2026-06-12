from rest_framework import serializers
from ..models import Supervisor
from .usuario_serializer import UsuarioSerializer
from .condominio_serializer import CondominioSerializer

class SupervisorSerializer(serializers.ModelSerializer):
    usuario_detalhe = UsuarioSerializer(source='usuario', read_only=True)
    # 🔥 Ajustado para many=True pois agora retorna uma lista de condomínios
    condominios_detalhe = CondominioSerializer(source='condominios', many=True, read_only=True)
    telefone_usuario = serializers.ReadOnlyField(source='usuario.telefone')
    class Meta:
        model = Supervisor
        fields = [
            'id', 'usuario', 'gestor', 'condominios','telefone_usuario'
            'data_criacao', 'usuario_detalhe', 'condominios_detalhe'
        ]
        read_only_fields = ['gestor','telefone_usuario']