from ninja import Router
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from ninja.responses import Response
from django.db import models
from typing import List
from .schemas import *
from core.utils.search_filter import search_filter
from pedido.models import Pedido as PedidoModel
from pedido.models import PedidoDetalle as PedidoDetalleModel
from usuario.auth import AuthBearer, es_admin, requiere_admin

router = Router(prefix='/pedidos', tags=['Pedidos'])


def _es_participante_o_admin(usuario, pedido: PedidoModel) -> bool:
	if not usuario:
		return False
	if es_admin(usuario):
		return True
	return pedido.creado_por_id == usuario.id or pedido.usuario_destino_id == usuario.id


def _puede_gestionar_pedido(usuario, pedido: PedidoModel) -> bool:
	if not usuario:
		return False
	if es_admin(usuario):
		return True
	return pedido.creado_por_id == usuario.id


@router.get('/listar_todos', response=List[Pedido], auth=AuthBearer())
@search_filter(['estado', 'creado_por__nombre', 'usuario_destino__nombre'])
@paginate
@requiere_admin
def listar_pedidos(request, busqueda: str = None):
	return PedidoModel.objects.order_by('-fecha_actualizacion')


@router.get('/mis_pedidos', response=List[Pedido], auth=AuthBearer())
@search_filter(['estado'])
@paginate
def listar_mis_pedidos(request, busqueda: str = None):
	usuario = request.auth
	return PedidoModel.objects.filter(
		models.Q(creado_por_id=usuario.id) | models.Q(usuario_destino_id=usuario.id)
	).order_by('-fecha_actualizacion')


@router.get('/obtener/{pedido_id}', response=Pedido, auth=AuthBearer())
def obtener_pedido(request, pedido_id: int):
	pedido = get_object_or_404(PedidoModel, id=pedido_id)
	if not _es_participante_o_admin(request.auth, pedido):
		return Response({'success': False, 'error': 'No autorizado'}, status=403)
	return pedido


@router.post('/crear', response=Pedido, auth=AuthBearer())
def crear_pedido(request, data: PedidoCreate):
	try:
		payload = data.dict()
		payload['creado_por'] = request.auth
		pedido = PedidoModel.objects.create(**payload)
		return pedido
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.patch('/actualizar/{pedido_id}', response=Pedido, auth=AuthBearer())
def actualizar_pedido(request, pedido_id: int, data: PedidoUpdate):
	try:
		pedido = get_object_or_404(PedidoModel, id=pedido_id)
		if not _puede_gestionar_pedido(request.auth, pedido):
			return Response({'success': False, 'error': 'No autorizado'}, status=403)

		for attr, value in data.dict(exclude_unset=True).items():
			setattr(pedido, attr, value)
		pedido.save()
		return pedido
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.patch('/cambiar_estado/{pedido_id}', response=Pedido, auth=AuthBearer())
def cambiar_estado_pedido(request, pedido_id: int, data: PedidoCambiarEstado):
	try:
		pedido = get_object_or_404(PedidoModel, id=pedido_id)
		if not _es_participante_o_admin(request.auth, pedido):
			return Response({'success': False, 'error': 'No autorizado'}, status=403)

		pedido.estado = data.estado
		pedido.save(update_fields=['estado', 'fecha_actualizacion'])
		return pedido
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.delete('/eliminar/{pedido_id}', auth=AuthBearer())
def eliminar_pedido(request, pedido_id: int):
	try:
		pedido = get_object_or_404(PedidoModel, id=pedido_id)
		if not _puede_gestionar_pedido(request.auth, pedido):
			return Response({'success': False, 'error': 'No autorizado'}, status=403)

		pedido.delete()
		return {'success': True}
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.get('/detalles/por_pedido/{pedido_id}', response=List[PedidoDetalle], auth=AuthBearer())
@search_filter(['producto__nombre'])
@paginate
def listar_detalles_por_pedido(request, pedido_id: int, busqueda: str = None):
	pedido = get_object_or_404(PedidoModel, id=pedido_id)
	if not _es_participante_o_admin(request.auth, pedido):
		return Response({'success': False, 'error': 'No autorizado'}, status=403)
	return PedidoDetalleModel.objects.filter(pedido_id=pedido_id).order_by('-fecha_actualizacion')


@router.post('/detalles/crear', response=PedidoDetalle, auth=AuthBearer())
def crear_detalle_pedido(request, data: PedidoDetalleCreate):
	try:
		pedido = get_object_or_404(PedidoModel, id=data.pedido_id)
		if not _puede_gestionar_pedido(request.auth, pedido):
			return Response({'success': False, 'error': 'No autorizado'}, status=403)

		detalle = PedidoDetalleModel.objects.create(**data.dict())
		return detalle
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.patch('/detalles/actualizar/{detalle_id}', response=PedidoDetalle, auth=AuthBearer())
def actualizar_detalle_pedido(request, detalle_id: int, data: PedidoDetalleUpdate):
	try:
		detalle = get_object_or_404(PedidoDetalleModel, id=detalle_id)
		if not _puede_gestionar_pedido(request.auth, detalle.pedido):
			return Response({'success': False, 'error': 'No autorizado'}, status=403)

		for attr, value in data.dict(exclude_unset=True).items():
			setattr(detalle, attr, value)
		detalle.save()
		return detalle
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.delete('/detalles/eliminar/{detalle_id}', auth=AuthBearer())
def eliminar_detalle_pedido(request, detalle_id: int):
	try:
		detalle = get_object_or_404(PedidoDetalleModel, id=detalle_id)
		if not _puede_gestionar_pedido(request.auth, detalle.pedido):
			return Response({'success': False, 'error': 'No autorizado'}, status=403)

		detalle.delete()
		return {'success': True}
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)
