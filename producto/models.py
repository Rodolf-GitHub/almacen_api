from django.db import models
from core.models import BaseModel
# Create your models here.
class Producto(BaseModel):
    proveedor = models.ForeignKey('proveedor.Proveedor', on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    categoria = models.ForeignKey('CategoriaProducto', on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    class Meta:
        db_table = 'producto'
        constraints = [
            models.UniqueConstraint(
                fields=['proveedor', 'nombre'],
                name='unique_producto_nombre_por_proveedor'
            )
        ]

class CategoriaProducto(BaseModel):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'categoria_producto'
