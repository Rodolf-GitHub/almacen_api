from ninja import Schema, ModelSchema
from typing import Optional

class Usuario(ModelSchema):
    class Meta:
        model = 'usuario.Usuario'
        exclude = ['contrasena_hasheada', 'token']

# solo para admin_general
class UsuarioCreate(Schema):
    nombre: str
    contrasena: str
    nombre_sucursal: str
    rol: Optional[str] = 'admin_sucursal'

# solo para admin_general
class UsuarioUpdate(Schema):
    nombre: Optional[str]
    contrasena: Optional[str]
    nombre_sucursal: Optional[str]
    rol: Optional[str]

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