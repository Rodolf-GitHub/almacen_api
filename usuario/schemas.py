from ninja import Schema, ModelSchema
from typing import Literal, Optional, Annotated
from pydantic import StringConstraints
from usuario.models import Usuario as UsuarioModel

Str50 = Annotated[str, StringConstraints(max_length=50)]

class Usuario(ModelSchema):
    class Meta:
        model = UsuarioModel
        exclude = ['contrasena_hasheada', 'token']

# solo para admin_general
class UsuarioCreate(Schema):
    nombre: Str50
    contrasena: Str50
    nombre_sucursal: Str50
    rol: Literal['admin_general', 'admin_sucursal'] = 'admin_sucursal'

# solo para admin_general
class UsuarioUpdate(Schema):
    nombre: Optional[Str50] = None
    contrasena: Optional[Str50] = None
    nombre_sucursal: Optional[Str50] = None
    rol: Optional[Literal['admin_general', 'admin_sucursal']] = None

class CambiarMiContrasena(Schema):
    contrasena_actual: Str50
    contrasena_nueva: Str50
    repetir_contrasena_nueva: Str50

class LoginRequest(Schema):
    nombre: Str50
    contrasena: Str50

class TokenResponse(Schema):
    token: Str50
    usuario : Usuario