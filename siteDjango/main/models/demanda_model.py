from django.db import models
from .condominio_model import Condominio
from .profissional_model import Profissional
from django.conf import settings

class Demanda(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_ANDAMENTO', 'Em andamento'),
        ('CONCLUIDA', 'Concluída'),
    ]
    URGENCIA_CHOICES = [
        ('URGENTE', 'Urgente'),
        ('NAO_URGENTE', 'Não urgente'),
    ]

    condominio = models.ForeignKey(Condominio, on_delete=models.CASCADE, related_name='demandas')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    urgencia = models.CharField(max_length=12, choices=URGENCIA_CHOICES, default='NAO_URGENTE')
    
    # Criador da demanda (pode ser Gestor ou Supervisor)
    criadoPor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='demandas_criadas')
    
    # Profissional acionado para o serviço
    profissionalAcionado = models.ForeignKey(Profissional, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE')
    dataAbertura = models.DateTimeField(auto_now_add=True)
    dataConclusao = models.DateTimeField(null=True, blank=True)
    previsaoConclusao = models.DateField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} - {self.condominio.nome}"