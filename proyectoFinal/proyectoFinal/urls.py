"""
URL configuration for proyectoFinal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from teloEnvio.views import RegistroView, LoginView, LandingPageView, PaginaInternaView, CatalogoIndex, CatalogoList, ProductosView, CrearProductoView, EditarProductoView, EliminarProductoView, ListaPedidosView, ActualizarEstadoPedidoView, AgregarPedido1View, AgregarPedido2View, AgregarPedido3View, VistaDetallesView, FinalizarPedidoView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='index'),
    path('catalogo', CatalogoIndex.as_view(), name='catalogo'), 
    path('catalogo/categoria/<int:id_categoria>', CatalogoList.as_view(), name='categoria'),
    path('registrarse', RegistroView.as_view(), name='registrarse'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('interno', PaginaInternaView.as_view(), name='paginaInterna'),
    path('interno/productos/', login_required(ProductosView.as_view()), name='productos'),
    path('interno/productos/agregar/', login_required(CrearProductoView.as_view()), name='agregar_producto'),
    path('interno/productos/<int:id_producto>/editar/', login_required(EditarProductoView.as_view()), name='editar_producto'),
    path('interno/productos/<int:pk>/eliminar/', login_required(EliminarProductoView.as_view()), name='eliminar_producto'),
    path('interno/pedidos', login_required(ListaPedidosView.as_view()), name = 'pedidos'),
    path('interno/pedidos/orden/<int:idpedido>', login_required(VistaDetallesView.as_view()), name='detalle_pedido'),
    path('interno/pedidos/orden/<int:idpedido>/modifica/estado', login_required(ActualizarEstadoPedidoView.as_view()), name='actualizarEstadoPedido'),
    path('interno/pedidos/agregar/1', login_required(AgregarPedido1View.as_view()), name='agregarPedido1'),
    path('interno/pedidos/agregar/2', login_required(AgregarPedido2View.as_view()), name='agregarPedido2'),
    path('interno/pedidos/agregar/3', login_required(AgregarPedido3View.as_view()), name='agregarPedido3'),
    path('interno/pedidos/cierre', login_required(FinalizarPedidoView.as_view()), name='cierre_pedidos')
]



# Configuración para servir archivos de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)