from ninja import Router
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from ninja.responses import Response
from typing import List
from .schemas import *
from core.utils.search_filter import search_filter
from proveedor.models import Proveedor as ProveedorModel
from usuario.auth import AuthBearer

router = Router(tags=['Proveedores'])


@router.get('/listar_todos', response=List[Proveedor])
@paginate
@search_filter(['nombre', 'telefono'])
def listar_proveedores(request, busqueda: str = None):
	return ProveedorModel.objects.order_by('-fecha_actualizacion')


@router.get('/obtener/{proveedor_id}', response=Proveedor)
def obtener_proveedor(request, proveedor_id: int):
	return get_object_or_404(ProveedorModel, id=proveedor_id)


@router.post('/crear', response=Proveedor, auth=AuthBearer())
def crear_proveedor(request, data: ProveedorCreate):
	try:
		payload = data.dict()
		payload['creado_por'] = request.auth
		proveedor = ProveedorModel.objects.create(**payload)
		return proveedor
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.patch('/actualizar/{proveedor_id}', response=Proveedor, auth=AuthBearer())
def actualizar_proveedor(request, proveedor_id: int, data: ProveedorUpdate):
	try:
		proveedor = get_object_or_404(ProveedorModel, id=proveedor_id)
		for attr, value in data.dict(exclude_unset=True).items():
			setattr(proveedor, attr, value)
		proveedor.save()
		return proveedor
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.delete('/eliminar/{proveedor_id}', auth=AuthBearer())
def eliminar_proveedor(request, proveedor_id: int):
	try:
		proveedor = get_object_or_404(ProveedorModel, id=proveedor_id)
		proveedor.delete()
		return {'success': True}
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)
