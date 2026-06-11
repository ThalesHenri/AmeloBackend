from django.db import models
from .demanda_model import Demanda
from django.conf import settings
class HistoricoAtualizacao(models.Model):
    demanda = models.ForeignKey(Demanda, on_delete=models.CASCADE, related_name='historicos')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    descricao_alteracao = models.TextField() # Ex: "Alterou o status da demanda para Em andamento."
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.data_registro} - {self.demanda.titulo}"
