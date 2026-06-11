from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Condominio(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='condominios')
    nome = models.CharField(max_length=150)
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)  # Ex: 'PB', 'SP'
    cep = models.CharField(max_length=9)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to='condominios/', blank=True, null=True)

    def __str__(self):
        return self.nome