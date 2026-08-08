from django.db import models
from .demanda_model import Demanda
from .historicoAtualizacao_model import HistoricoAtualizacao

class Anexo(models.Model):
    demanda = models.ForeignKey(Demanda, on_delete=models.CASCADE, related_name='anexos', blank=True, null=True)
    historico = models.ForeignKey(HistoricoAtualizacao, on_delete=models.CASCADE, related_name='anexos', blank=True, null=True)
    arquivo = models.FileField(upload_to='anexos_demandas/')
    dataCriacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Anexo para {self.demanda.titulo if self.demanda else 'Histórico'} - {self.arquivo.name}"


#ToDo - PRECISO ALTERAR TODOS OS CAMPOS PARA CAMEL CASE, POIS O FLUTTER NÃO ACEITA CAMPO COM UNDERLINE