from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from ninja import NinjaAPI

from usuario.api import router as usuario_router
from proveedor.api import router as proveedor_router
from producto.api import router as producto_router
from pedido.api import router as pedido_router
from dashboard.api import router as dashboard_router


api = NinjaAPI(title='Almacen API')

api.add_router('/usuarios', usuario_router)
api.add_router('/proveedores', proveedor_router)
api.add_router('/productos', producto_router)
api.add_router('/pedidos', pedido_router)
api.add_router('/dashboard', dashboard_router)

urlpatterns = [
    path('api/', api.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
