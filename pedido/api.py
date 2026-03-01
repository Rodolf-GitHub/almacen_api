from ninja import Router
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from ninja.responses import Response
from django.db import models
from typing import List, Optional
from .schemas import *
from core.utils.search_filter import search_filter
from pedido.models import Pedido as PedidoModel
from pedido.models import PedidoDetalle as PedidoDetalleModel
from proveedor.models import Proveedor as ProveedorModel
from usuario.auth import AuthBearer, es_admin, requiere_admin

router = Router(tags=['Pedidos'])


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


def _construir_resumen_copia_pedido(pedido: PedidoModel, proveedor: Optional[ProveedorModel] = None) -> dict:
	detalles = PedidoDetalleModel.objects.filter(pedido_id=pedido.id).select_related('producto', 'producto__proveedor').order_by('id')

	if proveedor:
		detalles = detalles.filter(producto__proveedor_id=proveedor.id)

	productos = []
	cantidad_total = 0
	proveedores_map = {}

	for detalle in detalles:
		cantidad_total += detalle.cantidad
		producto_item = {
			'producto_id': detalle.producto_id,
			'producto_nombre': detalle.producto.nombre,
			'cantidad': detalle.cantidad,
			'fecha_creacion': detalle.fecha_creacion,
		}
		productos.append(producto_item)

		if not proveedor:
			proveedor_id = detalle.producto.proveedor_id
			if proveedor_id not in proveedores_map:
				proveedores_map[proveedor_id] = {
					'proveedor_id': proveedor_id,
					'proveedor_nombre': detalle.producto.proveedor.nombre,
					'cantidad_total_productos': 0,
					'productos': [],
				}

			proveedores_map[proveedor_id]['cantidad_total_productos'] += detalle.cantidad
			proveedores_map[proveedor_id]['productos'].append(producto_item)

	return {
		'pedido_id': pedido.id,
		'estado': pedido.estado,
		'creado_por_nombre': pedido.creado_por.nombre if pedido.creado_por_id else None,
		'usuario_destino_nombre': pedido.usuario_destino.nombre if pedido.usuario_destino_id else None,
		'proveedor_id': proveedor.id if proveedor else None,
		'proveedor_nombre': proveedor.nombre if proveedor else None,
		'fecha_creacion': pedido.fecha_creacion,
		'fecha_actualizacion': pedido.fecha_actualizacion,
		'cantidad_total_productos': cantidad_total,
		'productos': productos,
		'proveedores': list(proveedores_map.values()) if not proveedor else [],
	}


@router.get('/listar_todos', response=List[Pedido], auth=AuthBearer())
@paginate
@search_filter(['estado', 'creado_por__nombre', 'usuario_destino__nombre'])
@requiere_admin
def listar_pedidos(request, busqueda: str = None):
	return PedidoModel.objects.order_by('-fecha_actualizacion')


@router.get('/mis_pedidos_hechos', response=List[Pedido], auth=AuthBearer())
@paginate
@search_filter(['estado'])
def listar_mis_pedidos_hechos(request, busqueda: str = None):
	usuario = request.auth
	return PedidoModel.objects.filter(creado_por_id=usuario.id).order_by('-fecha_actualizacion')


@router.get('/mis_pedidos_recibidos', response=List[Pedido], auth=AuthBearer())
@paginate
@search_filter(['estado'])
def listar_mis_pedidos_recibidos(request, busqueda: str = None):
	usuario = request.auth
	return PedidoModel.objects.filter(usuario_destino_id=usuario.id).order_by('-fecha_actualizacion')


@router.get('/obtener/{pedido_id}', response=Pedido, auth=AuthBearer())
def obtener_pedido(request, pedido_id: int):
	pedido = get_object_or_404(PedidoModel, id=pedido_id)
	if not _es_participante_o_admin(request.auth, pedido):
		return Response({'success': False, 'error': 'No autorizado'}, status=403)
	return pedido


@router.get('/copiar_pedido/completo/{pedido_id}', response=PedidoCopiaResumen, auth=AuthBearer())
def copiar_pedido_completo(request, pedido_id: int):
	pedido = get_object_or_404(PedidoModel, id=pedido_id)
	if not _es_participante_o_admin(request.auth, pedido):
		return Response({'success': False, 'error': 'No autorizado'}, status=403)
	return _construir_resumen_copia_pedido(pedido)


@router.get('/copiar_pedido/por_proveedor/{pedido_id}/{proveedor_id}', response=PedidoCopiaResumen, auth=AuthBearer())
def copiar_pedido_por_proveedor(request, pedido_id: int, proveedor_id: int):
	pedido = get_object_or_404(PedidoModel, id=pedido_id)
	if not _es_participante_o_admin(request.auth, pedido):
		return Response({'success': False, 'error': 'No autorizado'}, status=403)

	proveedor = get_object_or_404(ProveedorModel, id=proveedor_id)
	return _construir_resumen_copia_pedido(pedido, proveedor=proveedor)


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


@router.get('/productos_pedido/por_pedido/{pedido_id}/proveedor/{proveedor_id}', response=List[PedidoDetalle], auth=AuthBearer())
@paginate
@search_filter(['producto__nombre'])
def listar_productos_pedido_por_proveedor(request, pedido_id: int, proveedor_id: int, busqueda: str = None):
	pedido = get_object_or_404(PedidoModel, id=pedido_id)
	if not _es_participante_o_admin(request.auth, pedido):
		return Response({'success': False, 'error': 'No autorizado'}, status=403)
	return PedidoDetalleModel.objects.filter(
		pedido_id=pedido_id,
		producto__proveedor_id=proveedor_id,
	).order_by('-fecha_actualizacion')


@router.get('/proveedores_resumen/por_pedido/{pedido_id}', response=List[PedidoProveedorResumen], auth=AuthBearer())
def listar_proveedores_resumen_por_pedido(request, pedido_id: int):
	pedido = get_object_or_404(PedidoModel, id=pedido_id)
	if not _es_participante_o_admin(request.auth, pedido):
		return Response({'success': False, 'error': 'No autorizado'}, status=403)

	proveedores = ProveedorModel.objects.order_by('nombre')
	resumen = []

	for proveedor in proveedores:
		cantidad = PedidoDetalleModel.objects.filter(
			pedido_id=pedido_id,
			producto__proveedor_id=proveedor.id,
		).aggregate(total=models.Sum('cantidad'))['total'] or 0

		resumen.append({
			'proveedor_id': proveedor.id,
			'proveedor_nombre': proveedor.nombre,
			'cantidad_productos_pedidos': cantidad,
		})

	return resumen


@router.post('/productos_pedido/crear', response=PedidoDetalle, auth=AuthBearer())
def crear_producto_pedido(request, data: PedidoDetalleCreate):
	try:
		pedido = get_object_or_404(PedidoModel, id=data.pedido_id)
		if not _puede_gestionar_pedido(request.auth, pedido):
			return Response({'success': False, 'error': 'No autorizado'}, status=403)

		producto_pedido = PedidoDetalleModel.objects.create(**data.dict())
		return producto_pedido
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.patch('/productos_pedido/actualizar/{producto_pedido_id}', response=PedidoDetalle, auth=AuthBearer())
def actualizar_producto_pedido(request, producto_pedido_id: int, data: PedidoDetalleUpdate):
	try:
		producto_pedido = get_object_or_404(PedidoDetalleModel, id=producto_pedido_id)
		if not _puede_gestionar_pedido(request.auth, producto_pedido.pedido):
			return Response({'success': False, 'error': 'No autorizado'}, status=403)

		for attr, value in data.dict(exclude_unset=True).items():
			setattr(producto_pedido, attr, value)
		producto_pedido.save()
		return producto_pedido
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.delete('/productos_pedido/eliminar/{producto_pedido_id}', auth=AuthBearer())
def eliminar_producto_pedido(request, producto_pedido_id: int):
	try:
		producto_pedido = get_object_or_404(PedidoDetalleModel, id=producto_pedido_id)
		if not _puede_gestionar_pedido(request.auth, producto_pedido.pedido):
			return Response({'success': False, 'error': 'No autorizado'}, status=403)

		producto_pedido.delete()
		return {'success': True}
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)
