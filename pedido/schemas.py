from ninja import Schema, ModelSchema
from typing import Optional
from typing import Literal

from pedido.models import Pedido as PedidoModel
from pedido.models import PedidoDetalle as PedidoDetalleModel


class Pedido(ModelSchema):
	creado_por_nombre: Optional[str] = None
	usuario_destino_nombre: Optional[str] = None

	class Meta:
		model = PedidoModel
		fields = '__all__'

	@staticmethod
	def resolve_creado_por_nombre(obj):
		if not obj.creado_por_id:
			return None
		return obj.creado_por.nombre

	@staticmethod
	def resolve_usuario_destino_nombre(obj):
		if not obj.usuario_destino_id:
			return None
		return obj.usuario_destino.nombre


class PedidoCreate(Schema):
	usuario_destino_id: Optional[int] = None
	estado: Literal['pendiente', 'completado'] = 'pendiente'


class PedidoUpdate(Schema):
	usuario_destino_id: Optional[int] = None


class PedidoCambiarEstado(Schema):
	estado: Literal['pendiente', 'completado']


class PedidoDetalle(ModelSchema):
	producto_nombre: Optional[str] = None
	producto_imagen: Optional[str] = None

	class Meta:
		model = PedidoDetalleModel
		fields = '__all__'

	@staticmethod
	def resolve_producto_nombre(obj):
		if not obj.producto_id:
			return None
		return obj.producto.nombre

	@staticmethod
	def resolve_producto_imagen(obj):
		if not obj.producto_id or not obj.producto.imagen:
			return None
		return obj.producto.imagen.url


class PedidoDetalleCreate(Schema):
	pedido_id: int
	producto_id: int
	cantidad: int


class PedidoDetalleUpdate(Schema):
	cantidad: Optional[int] = None


class PedidoProveedorResumen(Schema):
	proveedor_id: int
	proveedor_nombre: str
	cantidad_productos_pedidos: int
