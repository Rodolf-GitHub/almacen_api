from django.db import models
from core.models import BaseModel
# Create your models here.
class Proveedor(BaseModel):
    nombre = models.CharField(max_length=50,unique=True)
    telefono = models.CharField(max_length=50,null=True, blank=True)
    creado_por = models.ForeignKey('usuario.Usuario', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'proveedor'
