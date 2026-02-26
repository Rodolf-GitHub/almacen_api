from django.db import models
from core.models import BaseModel
# Create your models here.
class Usuario(BaseModel):
    nombre = models.CharField(max_length=15,unique=True)
    contraseña = models.CharField(max_length=100)
    nombre_sucursal = models.CharField(max_length=100)
    token = models.CharField(max_length=128, blank=True, null=True)
    rol = models.CharField(max_length=20, default='admin_sucursal')

    class Meta:
        db_table = 'usuario'
