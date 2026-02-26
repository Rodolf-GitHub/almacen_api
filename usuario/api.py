from ninja import Router
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from ninja.responses import Response
from typing import List
from .schemas import *
from core.utils.search_filter import search_filter
from usuario.auth import AuthBearer, GenerateToken, requiere_admin
from usuario.models import Usuario as UsuarioModel

router = Router(tags=['Usuarios'])


@router.post('/login', response=TokenResponse, auth=None)
def login(request, data: LoginRequest):
	try:
		usuario = UsuarioModel.objects.filter(nombre=data.nombre).first()
		if not usuario or not check_password(data.contrasena, usuario.contrasena_hasheada):
			return Response({'success': False, 'error': 'Credenciales inválidas'}, status=401)

		usuario.token = GenerateToken.generate()
		usuario.save(update_fields=['token', 'fecha_actualizacion'])
		return {'token': usuario.token, 'usuario': usuario}
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.post('/logout', auth=AuthBearer())
def logout(request):
	try:
		usuario = request.auth
		if not usuario:
			return Response({'success': False, 'error': 'No autenticado'}, status=401)

		usuario.token = None
		usuario.save(update_fields=['token', 'fecha_actualizacion'])
		return {'success': True}
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.get('/mi_perfil', response=Usuario, auth=AuthBearer())
def mi_perfil(request):
	usuario = request.auth
	if not usuario:
		return Response({'success': False, 'error': 'No autenticado'}, status=401)
	return usuario


@router.get('/listar_todos', response=List[Usuario], auth=AuthBearer())
@search_filter(['nombre', 'nombre_sucursal', 'rol'])
@paginate
@requiere_admin
def listar_usuarios(request, busqueda: str = None):
	return UsuarioModel.objects.order_by('-fecha_actualizacion')


@router.get('/listar_sucursales', response=List[Usuario], auth=None)
@search_filter(['nombre', 'nombre_sucursal'])
@paginate
def listar_sucursales(request, busqueda: str = None):
	return UsuarioModel.objects.exclude(rol=UsuarioModel.RolChoices.ADMIN_GENERAL).order_by('-fecha_actualizacion')


@router.get('/obtener/{usuario_id}', response=Usuario, auth=None)
def obtener_usuario(request, usuario_id: int):
	usuario = get_object_or_404(UsuarioModel, id=usuario_id)
	return usuario


@router.post('/crear', response=Usuario, auth=AuthBearer())
@requiere_admin
def crear_usuario(request, data: UsuarioCreate):
	try:
		data_dict = data.dict()
		data_dict['contrasena_hasheada'] = make_password(data_dict.pop('contrasena'))
		usuario = UsuarioModel.objects.create(**data_dict)
		return usuario
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.patch('/actualizar/{usuario_id}', response=Usuario, auth=AuthBearer())
@requiere_admin
def actualizar_usuario(request, usuario_id: int, data: UsuarioUpdate):
	try:
		usuario = get_object_or_404(UsuarioModel, id=usuario_id)
		payload = data.dict(exclude_unset=True)

		if 'contrasena' in payload:
			payload['contrasena_hasheada'] = make_password(payload.pop('contrasena'))

		for attr, value in payload.items():
			setattr(usuario, attr, value)

		usuario.save()
		return usuario
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.post('/cambiar_mi_contrasena', auth=AuthBearer())
def cambiar_mi_contrasena(request, data: CambiarMiContrasena):
	try:
		usuario = request.auth
		if not usuario:
			return Response({'success': False, 'error': 'No autenticado'}, status=401)

		if data.contrasena_nueva != data.repetir_contrasena_nueva:
			return Response({'success': False, 'error': 'La nueva contraseña no coincide'}, status=400)

		if not check_password(data.contrasena_actual, usuario.contrasena_hasheada):
			return Response({'success': False, 'error': 'La contraseña actual es incorrecta'}, status=400)

		usuario.contrasena_hasheada = make_password(data.contrasena_nueva)
		usuario.save(update_fields=['contrasena_hasheada', 'fecha_actualizacion'])
		return {'success': True}
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)


@router.delete('/eliminar/{usuario_id}', auth=AuthBearer())
@requiere_admin
def eliminar_usuario(request, usuario_id: int):
	try:
		usuario = get_object_or_404(UsuarioModel, id=usuario_id)
		usuario.delete()
		return {'success': True}
	except Exception as e:
		return Response({'success': False, 'error': str(e)}, status=400)



