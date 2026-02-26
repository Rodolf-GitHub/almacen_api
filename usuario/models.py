from django.db import models
from core.models import BaseModel
# Create your models here.
class Usuario(BaseModel):
    nombre = models.CharField(max_length=15,unique=True)
    contrasena_hasheada = models.CharField(max_length=100)
    nombre_sucursal = models.CharField(max_length=100)
    token = models.CharField(max_length=128, blank=True, null=True)
    class RolChoices(models.TextChoices):
        ADMIN_GENERAL = 'admin_general', 'Admin General'
        ADMIN_SUCURSAL = 'admin_sucursal', 'Admin Sucursal'
    rol = models.CharField(max_length=20, choices=RolChoices.choices, default=RolChoices.ADMIN_SUCURSAL)

    class Meta:
        db_table = 'usuario'
