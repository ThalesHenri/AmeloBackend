# supervisor_serializer.py
from rest_framework import serializers
from ..models import Supervisor
from .usuario_serializer import UsuarioSerializer
from .condominio_serializer import CondominioSerializer


class SupervisorSerializer(serializers.ModelSerializer):
    ativo = serializers.BooleanField(required=False)
    usuario = UsuarioSerializer()
    usuarioDetalhe = UsuarioSerializer(source='usuario', read_only=True)
    condominiosDetalhe = CondominioSerializer(source='condominios', many=True, read_only=True)
    telefoneUsuario = serializers.ReadOnlyField(source='usuario.telefone')

    class Meta:
        model = Supervisor
        fields = [
            'id',
            'ativo',
            'usuario',
            'gestor',
            'condominios',
            'telefoneUsuario',
            'dataCriacao',
            'usuarioDetalhe',
            'condominiosDetalhe',
        ]
        read_only_fields = ['gestor', 'telefoneUsuario', 'dataCriacao', 'usuarioDetalhe', 'condominiosDetalhe']

    def to_internal_value(self, data):
        # 🔑 Em updates, informa ao campo 'usuario' aninhado qual é a instância
        # atual, para que o UniqueValidator do username exclua o próprio
        # registro da checagem (senão ele sempre acusa duplicidade em edição).
        if self.instance is not None:
            self.fields['usuario'].instance = self.instance.usuario
        return super().to_internal_value(data)