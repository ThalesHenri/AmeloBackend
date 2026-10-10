from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLE_CHOICES = [
        ('GESTOR', 'Gestor'),
        ('SUPERVISOR', 'Supervisor'),
    ]
    
    role = models.CharField(
        max_length=15, 
        choices=ROLE_CHOICES, 
        default='GESTOR'
    )
    
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    senha_redefinida = models.BooleanField(default=False)
    def get_role_display(self):
        if self.role == 'GESTOR':
            return 'Gestor'
        elif self.role == 'SUPERVISOR':
            return 'Supervisor'
        return 'Desconecido'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"