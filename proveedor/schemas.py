from ninja import Schema, ModelSchema
from typing import Optional
from proveedor.models import Proveedor as ProveedorModel


class Proveedor(ModelSchema):
	class Meta:
		model = ProveedorModel
		fields = '__all__'


class ProveedorCreate(Schema):
	nombre: str
	telefono: Optional[str] = None


class ProveedorUpdate(Schema):
	nombre: Optional[str] = None
	telefono: Optional[str] = None


