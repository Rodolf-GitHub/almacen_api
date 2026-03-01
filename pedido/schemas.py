from ninja import Schema, ModelSchema
from typing import Optional, Annotated
from typing import Literal
from typing import List
from datetime import datetime
from django.db.models import Sum
from pydantic import StringConstraints

from pedido.models import Pedido as PedidoModel
from pedido.models import PedidoDetalle as PedidoDetalleModel

Str50 = Annotated[str, StringConstraints(max_length=50)]


class Pedido(ModelSchema):
	creado_por_nombre: Optional[Str50] = None
	usuario_destino_nombre: Optional[Str50] = None
	cantidad_productos: int = 0

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

	@staticmethod
	def resolve_cantidad_productos(obj):
		return obj.detalles.aggregate(total=Sum('cantidad'))['total'] or 0


class PedidoCreate(Schema):
	usuario_destino_id: Optional[int] = None
	estado: Literal['pendiente', 'completado'] = 'pendiente'


class PedidoUpdate(Schema):
	usuario_destino_id: Optional[int] = None


class PedidoCambiarEstado(Schema):
	estado: Literal['pendiente', 'completado']


class PedidoDetalle(ModelSchema):
	producto_nombre: Optional[Str50] = None
	producto_imagen: Optional[Str50] = None

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
	proveedor_nombre: Str50
	cantidad_productos_pedidos: int


class PedidoCopiaItem(Schema):
	proveedor_id: int
	proveedor_nombre: Str50
	producto_id: int
	producto_nombre: Str50
	cantidad: int
	fecha_creacion: datetime


class PedidoCopiaResumen(Schema):
	pedido_id: int
	estado: Str50
	creado_por_nombre: Optional[Str50] = None
	usuario_destino_nombre: Optional[Str50] = None
	proveedor_id: Optional[int] = None
	proveedor_nombre: Optional[Str50] = None
	fecha_creacion: datetime
	fecha_actualizacion: datetime
	cantidad_total_productos: int
	productos: List[PedidoCopiaItem] = []
