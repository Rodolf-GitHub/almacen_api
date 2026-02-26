from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from usuario.models import Usuario


class Command(BaseCommand):
    help = "Crea (o promueve) un usuario con rol admin_general"

    def add_arguments(self, parser):
        parser.add_argument('--nombre', required=True, help='Nombre de usuario')
        parser.add_argument('--contrasena', required=True, help='Contraseña en texto plano')
        parser.add_argument('--sucursal', required=True, help='Nombre de sucursal')

    def handle(self, *args, **options):
        nombre = options['nombre']
        contrasena = options['contrasena']
        sucursal = options['sucursal']

        usuario = Usuario.objects.filter(nombre=nombre).first()

        if usuario:
            usuario.contrasena_hasheada = make_password(contrasena)
            usuario.nombre_sucursal = sucursal
            usuario.rol = Usuario.RolChoices.ADMIN_GENERAL
            usuario.token = None
            usuario.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario actualizado como admin_general: {usuario.nombre}'))
            return

        usuario = Usuario.objects.create(
            nombre=nombre,
            contrasena_hasheada=make_password(contrasena),
            nombre_sucursal=sucursal,
            rol=Usuario.RolChoices.ADMIN_GENERAL,
            token=None,
        )
        self.stdout.write(self.style.SUCCESS(f'Usuario admin_general creado: {usuario.nombre}'))
