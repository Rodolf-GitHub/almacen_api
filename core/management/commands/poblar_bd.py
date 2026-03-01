import random
import time
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from producto.models import Producto
from proveedor.models import Proveedor


class Command(BaseCommand):
    help = 'Puebla la base de datos con proveedores y productos aleatorios.'

    def add_arguments(self, parser):
        parser.add_argument('--proveedores', type=int, default=1000, help='Cantidad de proveedores a crear')
        parser.add_argument(
            '--productos-por-proveedor',
            type=int,
            default=1000,
            help='Cantidad de productos a crear por proveedor',
        )
        parser.add_argument('--batch-size', type=int, default=2000, help='Tamaño de lote para bulk_create')
        parser.add_argument('--seed', type=int, default=None, help='Semilla opcional para reproducibilidad')

    def handle(self, *args, **options):
        cantidad_proveedores = options['proveedores']
        productos_por_proveedor = options['productos_por_proveedor']
        batch_size = options['batch_size']
        seed = options['seed']

        if cantidad_proveedores <= 0:
            raise CommandError('--proveedores debe ser mayor a 0')
        if productos_por_proveedor <= 0:
            raise CommandError('--productos-por-proveedor debe ser mayor a 0')
        if batch_size <= 0:
            raise CommandError('--batch-size debe ser mayor a 0')

        if seed is not None:
            random.seed(seed)

        total_productos_esperado = cantidad_proveedores * productos_por_proveedor
        marca_tiempo = timezone.now().strftime('%Y%m%d%H%M%S')

        self.stdout.write(
            self.style.WARNING(
                f'Iniciando carga: {cantidad_proveedores} proveedores y {total_productos_esperado} productos...'
            )
        )
        inicio = time.perf_counter()

        proveedores = []
        for index in range(cantidad_proveedores):
            nombre = f'PROV_{marca_tiempo}_{index + 1:04d}'
            telefono = f'09{random.randint(1000000, 9999999)}'
            proveedores.append(Proveedor(nombre=nombre, telefono=telefono))

        with transaction.atomic():
            Proveedor.objects.bulk_create(proveedores, batch_size=batch_size)

        proveedores_creados = list(
            Proveedor.objects.filter(nombre__startswith=f'PROV_{marca_tiempo}_').order_by('id')
        )

        if len(proveedores_creados) != cantidad_proveedores:
            raise CommandError('No se pudieron recuperar todos los proveedores creados para generar productos.')

        total_productos_creados = 0
        productos_lote = []

        with transaction.atomic():
            for idx_proveedor, proveedor in enumerate(proveedores_creados, start=1):
                for idx_producto in range(productos_por_proveedor):
                    precio_compra = Decimal(random.randint(100, 150000)) / Decimal('100')
                    factor_venta = Decimal(str(random.uniform(1.10, 2.20)))
                    precio_venta = (precio_compra * factor_venta).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                    productos_lote.append(
                        Producto(
                            proveedor=proveedor,
                            nombre=f'PROD_{proveedor.id}_{idx_producto + 1:04d}',
                            descripcion=f'Producto aleatorio {idx_producto + 1} del proveedor {proveedor.nombre}',
                            precio_compra=precio_compra,
                            precio_venta=precio_venta,
                        )
                    )

                    if len(productos_lote) >= batch_size:
                        Producto.objects.bulk_create(productos_lote, batch_size=batch_size)
                        total_productos_creados += len(productos_lote)
                        productos_lote = []

                if idx_proveedor % 50 == 0:
                    self.stdout.write(
                        f'Proveedores procesados: {idx_proveedor}/{cantidad_proveedores} | '
                        f'Productos creados: {total_productos_creados}'
                    )

            if productos_lote:
                Producto.objects.bulk_create(productos_lote, batch_size=batch_size)
                total_productos_creados += len(productos_lote)

        duracion = time.perf_counter() - inicio
        self.stdout.write(self.style.SUCCESS('Carga finalizada correctamente.'))
        self.stdout.write(f'Proveedores creados: {len(proveedores_creados)}')
        self.stdout.write(f'Productos creados: {total_productos_creados}')
        self.stdout.write(f'Tiempo total: {duracion:.2f} segundos')
