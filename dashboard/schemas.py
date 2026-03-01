from ninja import Schema, ModelSchema
from typing import Optional, Annotated
from datetime import datetime
from pydantic import StringConstraints

Str50 = Annotated[str, StringConstraints(max_length=50)]


class DashboardEstadisticas(Schema):
	fecha_hora_actual: datetime
	usuario_autenticado_nombre: Str50
	usuario_autenticado_sucursal: Str50
	cantidad_proveedores: int
	cantidad_productos: int
	cantidad_pedidos_hechos_pendientes: int
	cantidad_pedidos_hechos_completados: int
	cantidad_pedidos_recibidos_pendientes: int
	cantidad_pedidos_recibidos_completados: int
