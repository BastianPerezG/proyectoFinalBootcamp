from django.contrib import admin

# Register your models here.

from django.contrib import admin
from teloEnvio.models import Estado_Pedido, MetodoPago, Cliente, Productos, Pedidos,Categoria, Direcciones, CustomUser, Detalles_Pedido, Productor
from teloEnvio.form import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class CustomUserAdmin(UserAdmin):                   # Modelo de usuarios personalizados
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'run',
        'idCliente',
        'is_staff',
        ]
    ordering = ['id']
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('run', 'idCliente')}),)         # Edición de usuarios en la administración
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {'fields': ('run','idCliente')}),)  # Creación de usuarios en la administración

admin.site.register(CustomUser, CustomUserAdmin)


# Modelos tablas auxiliares

class Estado_Pedido_Admin(admin.ModelAdmin):        # Modelo de Estado de pedidos
    list_display = ['id', 'estado']
    search_fields = ['estado']
    ordering = ['id']
    fields = ['estado']

admin.site.register(Estado_Pedido, Estado_Pedido_Admin)


class MetodoPago_Admin(admin.ModelAdmin):           # Modelo de Métodos de pago
    list_display = ['id', 'nombre']
    search_fields = ['nombre']
    ordering = ['id']
    fields = ['nombre']

admin.site.register(MetodoPago, MetodoPago_Admin)


class Cliente_Admin(admin.ModelAdmin):             # Modelo de Clientes
    list_display = ['id', 'nombre', 'apellido', 'fono', 'correo']
    search_fields = ['id', 'nombre']
    ordering = ['id']
    fields = ['nombre', 'apellido', 'fono', 'correo']

admin.site.register(Cliente, Cliente_Admin)


class Productos_Admin(admin.ModelAdmin):            # Modelo de Productos
    list_display = ['id', 'nombre', 'descripcion', 'categoria', 'stock', 'precio', 'idProductor']
    list_filter = ['nombre', 'precio']
    search_fields = ['nombre']
    ordering = ['id']
    fields = ['nombre', 'descripcion', 'categoria', 'stock', 'precio', 'idProductor']

admin.site.register(Productos, Productos_Admin)


class Pedidos_Admin(admin.ModelAdmin):              # Modelo de Pedidos
    list_display = ['id', 'fecha_creacion', 'idMetodoPago', 'idEstado', 'idDireccion', 'idUsuario', 'idCliente']
    list_filter = ['fecha_creacion', 'idEstado', 'idUsuario', 'idCliente']
    search_fields = ['fecha_creacion', 'idEstado', 'idUsuario', 'idcliente']
    ordering = ['id']
    fields = ['fecha_creacion', 'idMetodoPago', 'idEstado', 'idDireccion', 'instrucciones_entrega', 'idUsuario', 'idCliente', 'total_pedido']

admin.site.register(Pedidos, Pedidos_Admin)


class Direcciones_Admin(admin.ModelAdmin):          # Modelo de direcciones
    list_display = ['id', 'idCliente', 'idProductor', 'direccion', 'numero', 'Comuna']
    list_filter = ['idCliente', 'Comuna']
    search_fields = ['idCliente', 'Comuna']
    ordering = ['id']
    fields = ['idCliente', 'idProductor', 'direccion', 'numero', 'Comuna', 'descripcion']

admin.site.register(Direcciones, Direcciones_Admin)


class DetallePedidos_Admin(admin.ModelAdmin):       # Modelo de detalles de pedido
    list_display = ['id', 'idPedidos', 'idProductos', 'cantidad', 'precio' ]
    list_filter = ['idPedidos']
    search_fields = ['idPedidos']
    ordering = ['id']
    fields = ['idPedidos', 'idProductos', 'cantidad', 'precio' ]

admin.site.register(Detalles_Pedido, DetallePedidos_Admin)


class Categorias_Admin(admin.ModelAdmin):
    list_display = ['id', 'nombre']
    search_fields = ['nombre']
    ordering = ['id']
    fields = ['nombre']

admin.site.register(Categoria, Categorias_Admin)

class Productor_Admin(admin.ModelAdmin):
    list_display = ['nombreContacto', 'rut', 'razonSocial', 'rubro']
    search_fields = ['id','nombreContacto']
    ordering = ['id']
    fields = ['nombreContacto', 'rut', 'razonSocial', 'rubro']

admin.site.register(Productor, Productor_Admin)