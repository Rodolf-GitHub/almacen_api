from functools import wraps
from ninja.responses import Response
from ninja.security import HttpBearer
from usuario.models import Usuario

def _append_doc_note(func, note: str) -> str:
    base = (getattr(func, "__doc__", "") or "").strip()
    if not base:
        return note
    if note in base:
        return base
    return f"{base}\n\n{note}"

def es_admin(usuario):
    return usuario.rol == Usuario.RolChoices.ADMIN_GENERAL

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            usuario = Usuario.objects.get(token=token)
            return usuario
        except Usuario.DoesNotExist:
            return None


class GenerateToken:
    @staticmethod
    def generate():
        import uuid

        return str(uuid.uuid4().hex)

def requiere_admin(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        usuario = request.auth
        if not usuario:
            return Response({"success": False, "error": "No autenticado"}, status=401)
        if not es_admin(usuario):
            return Response({"success": False, "error": "Se requiere rol admin"}, status=403)
        return func(request, *args, **kwargs)

    wrapper.__doc__ = _append_doc_note(func, "Permisos: requiere rol admin.")

    return wrapper
