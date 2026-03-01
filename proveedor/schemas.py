from ninja import Schema, ModelSchema
from typing import Optional, Annotated
from pydantic import StringConstraints
from proveedor.models import Proveedor as ProveedorModel

Str50 = Annotated[str, StringConstraints(max_length=50)]


class Proveedor(ModelSchema):
	class Meta:
		model = ProveedorModel
		fields = '__all__'


class ProveedorCreate(Schema):
	nombre: Str50
	telefono: Optional[Str50] = None


class ProveedorUpdate(Schema):
	nombre: Optional[Str50] = None
	telefono: Optional[Str50] = None


