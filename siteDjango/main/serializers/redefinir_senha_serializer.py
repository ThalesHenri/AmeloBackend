from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class RedefinirSenhaSerializer(serializers.Serializer):
    """Serializer para redefinição de senha do próprio usuário autenticado."""

    senha_atual = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
    )
    nova_senha = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        style={'input_type': 'password'},
    )
    confirmar_senha = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate_nova_senha(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        if attrs['nova_senha'] != attrs['confirmar_senha']:
            raise serializers.ValidationError({
                'confirmar_senha': 'As senhas não coincidem.'
            })
        return attrs
