from ninja import Schema, ModelSchema
from typing import Optional, Annotated
from decimal import Decimal
from pydantic import StringConstraints
from producto.models import Producto as ProductoModel
from producto.models import CategoriaProducto as CategoriaProductoModel

Str50 = Annotated[str, StringConstraints(max_length=50)]


class ProductoList(ModelSchema):
	proveedor_nombre: Optional[Str50] = None
	categoria_nombre: Optional[Str50] = None

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
	proveedor_nombre: Optional[Str50] = None
	categoria_nombre: Optional[Str50] = None

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
	nombre: Str50
	descripcion: Optional[Str50] = None
	precio_compra: Optional[Decimal] = None
	precio_venta: Optional[Decimal] = None
	categoria_id: Optional[int] = None


class ProductoUpdate(Schema):
	proveedor_id: Optional[int] = None
	nombre: Optional[Str50] = None
	descripcion: Optional[Str50] = None
	precio_compra: Optional[Decimal] = None
	precio_venta: Optional[Decimal] = None
	categoria_id: Optional[int] = None

class CategoriaProductoSchema(ModelSchema):
	class Meta:
		model = CategoriaProductoModel
		fields = '__all__'

class CategoriaProductoCreate(Schema):
	nombre: Str50


class CategoriaProductoUpdate(Schema):
	nombre: Optional[Str50] = None
