from django.db import models
from core.models import BaseModel
from usuario.models import Usuario
# Create your models here.
class Pedido(BaseModel):
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    usuario_destino = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_recibidos')
    estado = models.CharField(max_length=20, default='pendiente')# pendiente,completado

class PedidoDetalle(BaseModel):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('producto.Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()


