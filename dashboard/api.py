from ninja import Router
from django.utils import timezone

from .schemas import *
from usuario.auth import AuthBearer
from proveedor.models import Proveedor
from producto.models import Producto
from pedido.models import Pedido

router = Router(tags=['Dashboard'])


@router.get('/estadisticas', response=DashboardEstadisticas, auth=AuthBearer())
def obtener_estadisticas(request):
	usuario = request.auth

	return {
		'fecha_hora_actual': timezone.now(),
		'usuario_autenticado_nombre': usuario.nombre,
		'usuario_autenticado_sucursal': usuario.nombre_sucursal,
		'cantidad_proveedores': Proveedor.objects.count(),
		'cantidad_productos': Producto.objects.count(),
		'cantidad_pedidos_hechos_pendientes': Pedido.objects.filter(
			creado_por_id=usuario.id,
			estado=Pedido.EstadoChoices.PENDIENTE,
		).count(),
		'cantidad_pedidos_hechos_completados': Pedido.objects.filter(
			creado_por_id=usuario.id,
			estado=Pedido.EstadoChoices.COMPLETADO,
		).count(),
		'cantidad_pedidos_recibidos_pendientes': Pedido.objects.filter(
			usuario_destino_id=usuario.id,
			estado=Pedido.EstadoChoices.PENDIENTE,
		).count(),
		'cantidad_pedidos_recibidos_completados': Pedido.objects.filter(
			usuario_destino_id=usuario.id,
			estado=Pedido.EstadoChoices.COMPLETADO,
		).count(),
	}
