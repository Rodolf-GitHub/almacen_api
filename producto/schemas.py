from ninja import Schema, ModelSchema
from typing import Optional
from decimal import Decimal
from producto.models import Producto as ProductoModel


class Producto(ModelSchema):
	proveedor_nombre: Optional[str] = None

	class Meta:
		model = ProductoModel
		fields = '__all__'

	@staticmethod
	def resolve_proveedor_nombre(obj):
		if not obj.proveedor_id:
			return None
		return obj.proveedor.nombre


class ProductoCreate(Schema):
	proveedor_id: int
	nombre: str
	descripcion: Optional[str] = None
	precio_compra: Optional[Decimal] = None
	precio_venta: Optional[Decimal] = None


class ProductoUpdate(Schema):
	proveedor_id: Optional[int] = None
	nombre: Optional[str] = None
	descripcion: Optional[str] = None
	precio_compra: Optional[Decimal] = None
	precio_venta: Optional[Decimal] = None
