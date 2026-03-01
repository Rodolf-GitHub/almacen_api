from django.db import models
from core.models import BaseModel
# Create your models here.
class Pedido(BaseModel):
    class EstadoChoices(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        COMPLETADO = 'completado', 'Completado'

    creado_por = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE, related_name='pedidos_creados')
    usuario_destino = models.ForeignKey('usuario.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_recibidos')
    estado = models.CharField(max_length=50, choices=EstadoChoices.choices, default=EstadoChoices.PENDIENTE)

class PedidoDetalle(BaseModel):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('producto.Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['pedido', 'producto'],
                name='unique_producto_por_pedido'
            )
        ]


