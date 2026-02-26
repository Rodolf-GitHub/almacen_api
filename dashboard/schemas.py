from ninja import Schema, ModelSchema
from typing import Optional
from datetime import datetime


class DashboardEstadisticas(Schema):
	fecha_hora_actual: datetime
	usuario_autenticado_nombre: str
	usuario_autenticado_sucursal: str
	cantidad_proveedores: int
	cantidad_productos: int
	cantidad_pedidos_hechos_pendientes: int
	cantidad_pedidos_hechos_completados: int
	cantidad_pedidos_recibidos_pendientes: int
	cantidad_pedidos_recibidos_completados: int
