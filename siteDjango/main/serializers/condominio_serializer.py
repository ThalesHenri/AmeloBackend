from rest_framework import serializers
from ..models import Condominio

class CondominioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condominio
        fields = '__all__'
        read_only_fields = ['usuario']