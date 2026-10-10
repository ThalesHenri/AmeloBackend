from rest_framework import serializers
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'role',
            'telefone', 'senha_redefinida',
        ]
        read_only_fields = ['role', 'senha_redefinida']