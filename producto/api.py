from ninja import Router
from ninja import File, UploadedFile
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from ninja.responses import Response
from typing import List
from .schemas import *
from core.utils.search_filter import search_filter
from core.utils.compress_image import compress_image
from core.utils.delete_image_file import delete_image_file
from producto.models import Producto as ProductoModel
from usuario.auth import AuthBearer

router = Router(tags=['Productos'])


@router.get('/listar_por_proveedor/{proveedor_id}', response=List[ProductoList])
@paginate
@search_filter(['nombre', 'descripcion', 'categoria__nombre'])
def listar_productos_por_proveedor(request, proveedor_id: int, busqueda: str = None):
	return ProductoModel.objects.filter(proveedor_id=proveedor_id).select_related('proveedor', 'categoria').order_by('-fecha_actualizacion')


@router.get('/listar_todos', response=List[ProductoList])
@paginate
@search_filter(['nombre', 'descripcion', 'categoria__nombre'])
def listar_productos_todos(request, busqueda: str = None):
	return ProductoModel.objects.select_related('proveedor', 'categoria').order_by('-fecha_actualizacion')


@router.get('/obtener/{producto_id}', response=ProductoDetail)
def obtener_producto(request, producto_id: int):
	return get_object_or_404(ProductoModel.objects.select_related('proveedor', 'categoria'), id=producto_id)


@router.post('/crear', response=ProductoDetail, auth=AuthBearer())
def crear_producto(request, data: ProductoCreate, imagen: File[UploadedFile] = None):
	try:
		if ProductoModel.objects.count() >= 2000:
			return Response({'success': False, 'error': 'Límite de 2000 productos alcanzado, contacte con el programador.'}, status=400)

		existe = ProductoModel.objects.filter(
			proveedor_id=data.proveedor_id,
			nombre__iexact=data.nombre,
		).exists()
		if existe:
			return Response({'success': False, 'error': 'Ya existe un producto con ese nombre en este proveedor'}, status=400)

		producto = ProductoModel.objects.create(**data.dict())

		if imagen:
			imagen_comprimida = compress_image(imagen)
			producto.imagen.save(imagen.name, imagen_comprimida, save=True)

		return get_object_or_404(ProductoModel.objects.select_related('proveedor', 'categoria'), id=producto.id)
	except IntegrityError:
		return Response({'success': False, 'error': 'Ya existe un producto con ese nombre en este proveedor'}, status=400)
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.patch('/actualizar/{producto_id}', response=ProductoDetail, auth=AuthBearer())
def actualizar_producto(request, producto_id: int, data: ProductoUpdate, imagen: File[UploadedFile] = None):
	try:
		producto = get_object_or_404(ProductoModel, id=producto_id)
		payload = data.dict(exclude_unset=True)

		proveedor_id_final = payload.get('proveedor_id', producto.proveedor_id)
		nombre_final = payload.get('nombre', producto.nombre)
		existe = ProductoModel.objects.filter(
			proveedor_id=proveedor_id_final,
			nombre__iexact=nombre_final,
		).exclude(id=producto.id).exists()
		if existe:
			return Response({'success': False, 'error': 'Ya existe un producto con ese nombre en este proveedor'}, status=400)

		for attr, value in payload.items():
			setattr(producto, attr, value)

		if imagen:
			delete_image_file(producto.imagen)
			imagen_comprimida = compress_image(imagen)
			producto.imagen.save(imagen.name, imagen_comprimida, save=True)
		else:
			producto.save()

		return get_object_or_404(ProductoModel.objects.select_related('proveedor', 'categoria'), id=producto.id)
	except IntegrityError:
		return Response({'success': False, 'error': 'Ya existe un producto con ese nombre en este proveedor'}, status=400)
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.delete('/eliminar/{producto_id}', auth=AuthBearer())
def eliminar_producto(request, producto_id: int):
	try:
		producto = get_object_or_404(ProductoModel, id=producto_id)
		delete_image_file(producto.imagen)
		producto.delete()
		return {'success': True}
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)
