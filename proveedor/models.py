from django.db import models
from core.models import BaseModel
from usuario.models import Usuario
# Create your models here.
class Proveedor(BaseModel):
    nombre = models.CharField(max_length=100,unique=True)
    telefono = models.CharField(max_length=20,null=True, blank=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'proveedor'
