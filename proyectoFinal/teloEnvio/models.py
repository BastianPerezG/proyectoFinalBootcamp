from django.db import models

# Create your models here.

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


# Create your models here.
class Productor(models.Model):
    nombreContacto= models.CharField(max_length=45, null = False, blank = False)
    rut = models.CharField(max_length=12, null = False, blank = False)
    razonSocial = models.CharField(max_length=45, null = False, blank = False)
    rubro = models.CharField(max_length=45, null = False, blank = False)

    def __str__(self):
        return self.nombreContacto
    
    class Meta:
        verbose_name = 'Productor'
        verbose_name_plural = 'Productores'

class Productos(models.Model):              # Modelo de productos
    nombre = models.CharField(max_length=45, null=False, blank=False)
    descripcion = models.CharField(max_length=45, null=False, blank=False)
    stock = models.IntegerField(null=False, blank=False)
    precio = models.IntegerField(null=False, blank=False)
    image = models.ImageField(upload_to='product_images', default='default_image.png')
    categoria = models.ForeignKey('Categoria', default=1, on_delete=models.DO_NOTHING, null=False, blank = False)
    idProductor = models.ForeignKey('Productor', on_delete=models.DO_NOTHING, null=False, blank = False)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

class Categoria(models.Model):
    nombre = models.CharField(max_length=45, null=False, blank=False)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Categoría del Producto'
        verbose_name_plural = "Categorías de Productos"

class Estado_Pedido(models.Model):          # Modelo de estados de pedidos
    estado = models.CharField(max_length=45, null=False, blank=False)

    def __str__(self):
        return self.estado

    class Meta:
        verbose_name = 'Estado de pedido'
        verbose_name_plural = "Estado de pedidos"


class MetodoPago(models.Model):             # Modelo de métodos de pago
    nombre = models.CharField(max_length=45, null=False, blank=False)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Medio de pago'
        verbose_name_plural = 'Medios de pago'

class Cliente(models.Model):                # Modelo de clientes
    nombre = models.CharField(max_length=45, null=False, blank=False)
    apellido = models.CharField(max_length=45, null=False, blank=False)
    fono = models.CharField(max_length=12, null=False, blank=False)
    correo = models.CharField(max_length=45, null=False, blank=False)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

# Clase para usuarios personalizados
class CustomUser(AbstractUser):             # Modelo para usuarios personalizados
    run = models.CharField(max_length=12, null=False, blank=False)
    idCliente = models.ForeignKey(Cliente, on_delete=models.DO_NOTHING, null=True, blank = True)
    group = models.CharField(max_length=45, null=True)

    def __str__(self):
        return self.username

class Direcciones(models.Model):            # Modelo de direcciones
    idCliente = models.ForeignKey(Cliente, on_delete=models.DO_NOTHING, null=True, blank=True)
    idProductor = models.ForeignKey(Productor, on_delete=models.DO_NOTHING, null=True, blank=True)
    direccion = models.CharField(max_length=45, null=False, blank=False)
    numero = models.IntegerField(null=False, blank=False)
    Comuna = models.CharField(max_length=45, null=False, blank=False)
    descripcion = models.CharField(max_length=45, null=True, blank=True)

    def __str__(self):
        return (f'{self.direccion} {self.numero}, {self.Comuna}')
    
    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'


class Pedidos(models.Model):                # Modelo de pedidos
    fecha_creacion = models.DateTimeField(default=timezone.now)
    idMetodoPago = models.ForeignKey(MetodoPago, on_delete=models.DO_NOTHING, null=False, blank=False)
    idEstado = models.ForeignKey(Estado_Pedido, on_delete=models.DO_NOTHING, null=False, blank=False)
    idDireccion = models.ForeignKey(Direcciones, on_delete=models.DO_NOTHING, null=False, blank=False)
    idUsuario = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True, blank=True)
    idCliente = models.ForeignKey(Cliente, on_delete=models.DO_NOTHING, null=True, blank=True)
    instrucciones_entrega = models.CharField(max_length=100, null=True, blank=True)
    total_pedido = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'


class Detalles_Pedido(models.Model):        # Modelo de detalle de pedido
    idProductos = models.ForeignKey(Productos, on_delete=models.DO_NOTHING, null=False, blank=False)
    idPedidos = models.ForeignKey(Pedidos, on_delete=models.CASCADE, null=False, blank=False)
    cantidad = models.IntegerField(null=False, blank=False)
    precio = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Detalle de pedido'
        verbose_name_plural = 'Detalle de pedidos'

class Secciones(models.Model):
    class Meta:
        permissions = (
                        ("permiso_clientes", "Permisos necesarios para clientes"),
                        ("permiso_trabajadores", "Permisos necesarios para trabajadores"),
                    )