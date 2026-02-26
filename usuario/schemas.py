from ninja import Schema, ModelSchema
from typing import Literal, Optional
from usuario.models import Usuario as UsuarioModel

class Usuario(ModelSchema):
    class Meta:
        model = UsuarioModel
        exclude = ['contrasena_hasheada', 'token']

# solo para admin_general
class UsuarioCreate(Schema):
    nombre: str
    contrasena: str
    nombre_sucursal: str
    rol: Literal['admin_general', 'admin_sucursal'] = 'admin_sucursal'

# solo para admin_general
class UsuarioUpdate(Schema):
    nombre: Optional[str] = None
    contrasena: Optional[str] = None
    nombre_sucursal: Optional[str] = None
    rol: Optional[Literal['admin_general', 'admin_sucursal']] = None

class CambiarMiContrasena(Schema):
    contrasena_actual: str
    contrasena_nueva: str
    repetir_contrasena_nueva: str

class LoginRequest(Schema):
    nombre: str
    contrasena: str

class TokenResponse(Schema):
    token: str
    usuario : Usuario