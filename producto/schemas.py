from ninja import Schema, ModelSchema
from typing import Optional
from decimal import Decimal
from producto.models import Producto as ProductoModel
from producto.models import CategoriaProducto as CategoriaProductoModel


class ProductoList(ModelSchema):
	proveedor_nombre: Optional[str] = None
	categoria_nombre: Optional[str] = None

	class Meta:
		model = ProductoModel
		exclude = ['descripcion']

	@staticmethod
	def resolve_proveedor_nombre(obj):
		if not obj.proveedor_id:
			return None
		return obj.proveedor.nombre
	
	@staticmethod
	def resolve_categoria_nombre(obj):
		if not obj.categoria_id:
			return None
		return obj.categoria.nombre


class ProductoDetail(ModelSchema):
	proveedor_nombre: Optional[str] = None
	categoria_nombre: Optional[str] = None

	class Meta:
		model = ProductoModel
		fields = '__all__'

	@staticmethod
	def resolve_proveedor_nombre(obj):
		if not obj.proveedor_id:
			return None
		return obj.proveedor.nombre
	
	@staticmethod
	def resolve_categoria_nombre(obj):
		if not obj.categoria_id:
			return None
		return obj.categoria.nombre


class ProductoCreate(Schema):
	proveedor_id: int
	nombre: str
	descripcion: Optional[str] = None
	precio_compra: Optional[Decimal] = None
	precio_venta: Optional[Decimal] = None
	categoria_id: Optional[int] = None


class ProductoUpdate(Schema):
	proveedor_id: Optional[int] = None
	nombre: Optional[str] = None
	descripcion: Optional[str] = None
	precio_compra: Optional[Decimal] = None
	precio_venta: Optional[Decimal] = None
	categoria_id: Optional[int] = None

class CategoriaProductoSchema(ModelSchema):
	class Meta:
		model = CategoriaProductoModel
		fields = '__all__'

class CategoriaProductoCreate(Schema):
	nombre: str


class CategoriaProductoUpdate(Schema):
	nombre: Optional[str] = None
