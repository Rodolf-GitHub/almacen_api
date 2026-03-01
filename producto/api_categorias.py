from ninja import Router
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from ninja.responses import Response
from typing import List

from producto.models import CategoriaProducto as CategoriaProductoModel
from .schemas import CategoriaProductoSchema, CategoriaProductoUpdate
from core.utils.search_filter import search_filter


router = Router(tags=['Categorias Producto'])


@router.get('/listar_todas', response=List[CategoriaProductoSchema], auth=None)
@paginate
@search_filter(['nombre'])
def listar_categorias_producto(request):
	return CategoriaProductoModel.objects.order_by('nombre')


@router.patch('/actualizar/{categoria_id}', response=CategoriaProductoSchema, auth=None)
def actualizar_categoria_producto(request, categoria_id: int, data: CategoriaProductoUpdate):
	try:
		categoria = get_object_or_404(CategoriaProductoModel, id=categoria_id)
		for attr, value in data.dict(exclude_unset=True).items():
			setattr(categoria, attr, value)
		categoria.save()
		return categoria
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.delete('/eliminar/{categoria_id}', auth=None)
def eliminar_categoria_producto(request, categoria_id: int):
	try:
		categoria = get_object_or_404(CategoriaProductoModel, id=categoria_id)
		categoria.delete()
		return {'success': True}
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)