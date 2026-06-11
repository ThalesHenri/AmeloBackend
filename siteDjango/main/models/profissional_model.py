from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Profissional(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profissionais')
    nome = models.CharField(max_length=100)
    especialidade = models.CharField(max_length=100) # Ex: Hidráulica, Elétrica
    telefone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.nome} ({self.especialidade})"