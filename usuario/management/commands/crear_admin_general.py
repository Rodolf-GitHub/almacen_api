from getpass import getpass

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from usuario.models import Usuario


class Command(BaseCommand):
    help = "Crea (o promueve) un usuario con rol admin_general"

    def add_arguments(self, parser):
        parser.add_argument('--nombre', required=False, help='Nombre de usuario')
        parser.add_argument('--contrasena', required=False, help='Contraseña en texto plano')
        parser.add_argument('--sucursal', required=False, help='Nombre de sucursal')

    def _pedir_texto(self, etiqueta: str, valor_inicial: str | None = None) -> str:
        if valor_inicial:
            return valor_inicial.strip()

        while True:
            valor = input(f'{etiqueta}: ').strip()
            if valor:
                return valor
            self.stdout.write(self.style.ERROR(f'{etiqueta} es obligatorio.'))

    def _pedir_contrasena(self, valor_inicial: str | None = None) -> str:
        if valor_inicial:
            return valor_inicial

        while True:
            contrasena = getpass('Contraseña: ')
            repetir = getpass('Confirmar contraseña: ')

            if not contrasena:
                self.stdout.write(self.style.ERROR('La contraseña es obligatoria.'))
                continue

            if contrasena != repetir:
                self.stdout.write(self.style.ERROR('Las contraseñas no coinciden. Intenta nuevamente.'))
                continue

            return contrasena

    def handle(self, *args, **options):
        nombre = self._pedir_texto('Nombre', options.get('nombre'))
        contrasena = self._pedir_contrasena(options.get('contrasena'))
        sucursal = self._pedir_texto('Sucursal', options.get('sucursal'))

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
