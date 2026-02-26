from django.db import models
from core.models import BaseModel
# Create your models here.
class Producto(BaseModel):
    proveedor = models.ForeignKey('proveedor.Proveedor', on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=100,unique=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'producto'
