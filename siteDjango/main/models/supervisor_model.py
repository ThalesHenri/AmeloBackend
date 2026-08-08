from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Supervisor(models.Model):
    """Supervisor é um usuário do sistema vinculado a um Gestor."""
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='supervisor'
        )
    gestor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='supervisores'
        )
    condominios = models.ManyToManyField(
        'Condominio', 
        related_name='supervisores',
        blank=True
        )
    dataCriacao = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        # Garantir que o gestor não seja o mesmo que o supervisor
        if self.usuario == self.gestor:
            raise ValidationError("O supervisor não pode ser o mesmo que o gestor.")
        
        if self.usuario and self.usuario.role != 'SUPERVISOR':
            raise ValidationError("O usuário selecionado deve ter o papel de SUPERVISOR.")
        
        if self.gestor and self.gestor.role != 'GESTOR':
            raise ValidationError("O usuário selecionado como gestor deve ter o papel de GESTOR.")
    
    
    def save(self, *args, **kwargs):
        self.clean()  # Chama o método de validação antes de salvar
        super().save(*args, **kwargs)

    def __str__(self):
        
        return f"{self.usuario.get_full_name() or self.usuario.username} (Supervisor de {self.gestor.get_full_name() or self.gestor.username})"

