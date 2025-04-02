from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.core.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('administracao/', include('apps.administracao.urls')),
    path('carrinhos/', include('apps.carrinhos.urls')),
    path('pagamentos/', include('apps.pagamentos.urls')),
    path('pedidos/', include('apps.pedidos.urls')),
    path('produtos/', include('apps.produtos.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

