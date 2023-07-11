import os
import random
import string
from django.shortcuts import render, redirect, get_object_or_404, reverse
from teloEnvio.form import FormularioRegistro, FormularioLogin, FormularioProductos, FormularioEditarProductos, FormularioActualizarEstado, FormularioSeleccionCliente, FormularioCrearPedidos, FormularioCrearDetalle
from django.views.generic import TemplateView, DeleteView, View, FormView
from django.contrib.auth import authenticate, login
from teloEnvio.models import Pedidos, CustomUser, Cliente, Direcciones, Detalles_Pedido, Estado_Pedido, Productos, MetodoPago, Productor, Categoria
from django.core.mail import send_mail
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.base import ContentFile
from django.db.models import F, Sum
# Create your views here.

# Genera contraseñas aleatorias
def generate_random_password():
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(6))
    return password

# Create your views here.

#VIEWS PARA LOGIN Y REGISTRO
class LoginView(TemplateView):                                                              # Vista de acceso al sistema interno
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        formulario = FormularioLogin()
        title = 'Acceso al sitio interno'
        mensajes = request.session.get('mensajes', None)
        request.session.pop('mensajes', None)
        return render(request, self.template_name, {'formulario': formulario, 'title': title, 'mensajes': mensajes,})

    def post(self, request, *args, **kwargs):
        title = 'Acceso al sitio interno'
        form = FormularioLogin(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = CustomUser.objects.filter(email=email).first()
            if user is not None:
                if user.is_active:
                    authenticated_user = authenticate(request, username=user.username, password=password)
                    login(request, authenticated_user)
                    return redirect('paginaInterna')
            form.add_error('email', 'Se han ingresado las credenciales equivocadas.')
        return render(request, self.template_name, {'form': form, 'title': title})
    

class RegistroView(TemplateView):                                                           # Crea usuarios
    template_name = 'registrarse.html'

    def get(self, request, *args, **kwargs):
        context = {
            'formulario': FormularioRegistro(),
            'title': 'Registro de Usuario',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = FormularioRegistro(request.POST, request.FILES)
        title = 'Registro de Usuarios'
        if form.is_valid():
            username = form.cleaned_data['username']
            password = generate_random_password()
            user = form.save(commit=False)
            user.set_password(password)
            user.save()
            group = form.cleaned_data['group']
            if group:
                group.user_set.add(user)
            # mensajes = {'enviado': True, 'resultado': 'Has creado un nuevo usuario exitosamente'}
            request.session['mensajes'] = {'enviado': True, 'resultado': 'El usuario ha sido creado, tus datos de identificación se enviarán por email'}
            correo_destino = form.cleaned_data['email']
            mensaje = f'''
                Bienvenido {username} al Sistema de TeloEnvío.
                Gracias por registrarte en nuestro sitio web. A continuación se le adjunta su contraseña de acceso
                Contraseña :   {password} 
                Muchas Gracias por su preferencia
            '''
            send_mail(
                '[TE LO ENVIO] - Contraseña',
                mensaje,
                os.environ.get('EMAIL_HOST_USER'),  # Usar el correo configurado en settings.py
                [correo_destino],  # Enviar el correo al destinatario ingresado por el usuario
                fail_silently=False
            )            
            return redirect('login')  # Redirigir al formulario de inicio de sesión
        mensajes = {'enviado': False, 'resultado': form.errors}
        context = {
            'formulario': form,
            'mensajes': mensajes,
            'title': title
        }
        return render(request, self.template_name, context)
    


#VIEWS PARA EL SISTEMA EXTERNO, Lading, Catalogo
class LandingPageView(TemplateView):
    template_name = 'landing_page.html'

    def get(self, request, *args, **kwargs):
        title = 'Bienvenido a TeLoEnvío'
        return render(request, self.template_name, {'title': title})

class CatalogoIndex(TemplateView):
    template_name = 'catalogo.html'

    def get(self, request, *args, **kwargs):
        
        context = {
                'title' : 'Catálogo',
                'categorias': Categoria.objects.all().order_by('nombre'),
        }
        return render(request, self.template_name, context)
    
class CatalogoList(TemplateView):
    template_name = 'categoria.html'

    def get(self, request, *args, **kwargs):
        productos = Productos.objects.filter(categoria=self.kwargs['id_categoria']).order_by('id')
        context = {
                'title' : 'Catálogo',
                'categorias': Categoria.objects.all().order_by('nombre'),
                'categoria': Categoria.objects.get(id=self.kwargs['id_categoria']),
                'productos': productos,
                'cantidad_productos': len(productos),
        }
        return render(request, self.template_name, context)
    


# PAGINAS INTERNAS 

class PaginaInternaView(TemplateView):                                                            # Vista de pagina principal interna
    template_name = 'paginaInterna.html'
    def get(self, request, *args, **kwargs):
        primer_nombre = request.user.first_name
        apellido = request.user.last_name
        context = {
            'title': 'Bienvenido al sistema interno de TeLoEnvio',
            'primer_nombre': primer_nombre,
            'apellido': apellido
        }
        return render(request, self.template_name, context)

# CRUD PRODUCTOS

class ProductosView(PermissionRequiredMixin, TemplateView):                                 # Lista los productos
    template_name = 'productos.html'
    permission_required = "teloEnvio.permiso_trabajadores"
    def get(self, request, *args, **kwargs):
        context = {
            'title': 'Gestión de Productos',
            'productos': Productos.objects.all().order_by('id'),
            'mensajes' : request.session.get('mensajes', None),
        }
        request.session.pop('mensajes', None)
        return render(request, self.template_name, context)

class CrearProductoView(PermissionRequiredMixin, TemplateView):                            # Crea producto
    template_name = 'añadir_producto.html'
    permission_required = "teloEnvio.permiso_trabajadores"
    def get(self, request, *args, **kwargs):

        context = {
            'title': 'Añadir un nuevo Producto',
            'form': FormularioProductos(),
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = FormularioProductos(request.POST, request.FILES)
        if form.is_valid():
            if 'image' in request.FILES:
                image = request.FILES.get('image')
            else:
                image = form.ruta_fotoPerfil()

            registro = Productos(
                nombre= form.cleaned_data['nombre'],
                descripcion= form.cleaned_data['descripcion'],
                precio= form.cleaned_data['precio'],
                stock= form.cleaned_data['stock'],
                categoria = form.cleaned_data['idCategoria'],
                idProductor = form.cleaned_data['idProductor'],
                image = image
            )
            registro.save()
            request.session['mensajes'] = {'enviado': True, 'resultado': 'Has añadido un nuevo producto exitosamente'}
            return redirect('productos')
        else:
            mensajes = {'enviado': False, 'resultado': form.errors}
        context = {
            'title': 'Añadir un nuevo Producto',
            'mensajes': mensajes,
            'form': form
        }
        return render(request, self.template_name, context)


class EditarProductoView(PermissionRequiredMixin, TemplateView):                              # Edición de productos
    template_name = 'editar_producto.html'
    permission_required = "teloEnvio.permiso_trabajadores"

    def get(self, request, *args, **kwargs):
        id_producto = kwargs['id_producto']
        try:
            producto = Productos.objects.get(id=id_producto)
        except Productos.DoesNotExist:
            return render(request, 'elemento_no_existe.html')
        form = FormularioEditarProductos(instance=producto)
        context = {
            'title': 'Editar Producto Seleccionado',
            'form': form,
            'id_producto': id_producto,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        id_producto = kwargs['id_producto']
        try:
            producto = Productos.objects.get(id=id_producto)
        except Productos.DoesNotExist:
            return render(request, 'elemento_no_existe.html')
        form = FormularioEditarProductos(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            # Opcional: Puedes realizar acciones adicionales después de guardar la actualización
            request.session['mensajes'] = {'enviado': True, 'resultado': 'Has editado la información del producto seleccionado exitosamente'}
            return redirect('productos')
        else:
            context = {
                'title': 'Editar Producto Seleccionado',
                'form': form,
                'id_producto': id_producto,
            }
            return render(request, self.template_name, context)
    
class EliminarProductoView(PermissionRequiredMixin, DeleteView):                              # Elimina productos

    model = Productos
    permission_required = "teloEnvio.permiso_trabajadores"
    template_name = 'eliminar_producto.html'
    
    def get_success_url(self):
        return reverse('productos')
    
#CRUD PEDIDOS

class ListaPedidosView(TemplateView):                                                            # Vista de todos los pedidos
    template_name = 'pedidos.html'
    def get(self, request, *args, **kwargs):
        request.session.pop('mensajes', None)
        if request.user.groups.first().id == 1:
            pedidos = Pedidos.objects.filter(idCliente_id=request.user.idCliente_id).order_by('id').filter(idUsuario_id=request.user.id)
        else:
            pedidos = Pedidos.objects.all()
        context ={
            'title': 'Gestión de pedidos',
            'pedidos': pedidos
        }
        return render(request,self.template_name, context)

class AgregarPedido1View(FormView):
    template_name = 'agregarPedido1.html'
    form_class = FormularioCrearPedidos
    success_url = 'agregarpedido2'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.groups.first().id == 1:
            cliente = Cliente.objects.get(id=self.request.user.idCliente_id)
        else:
            cliente = Cliente.objects.all().first()  # Obtén una instancia de cliente (puedes ajustar esto según tu lógica)

        direcciones = Direcciones.objects.all()
        metodospago = MetodoPago.objects.all()

        context['title'] = 'Crear pedido'
        context['subtitle'] = 'Seleccione un Cliente'
        context['usuario'] = self.request.user.groups.first().id
        context['cliente'] = cliente
        context['direcciones_choices'] = direcciones
        context['metodospago_choices'] = metodospago

        self.request.session.pop('idCliente', None)
        
        return context

    def form_valid(self, form):
        idCliente = form.cleaned_data['idCliente'].id
        self.request.session['idCliente'] = idCliente
        self.request.session['mensajes'] = {'enviado': True, 'resultado': 'Se ha seleccionado un cliente, ahora hay que completar algunos datos'}
        return super().form_valid(form)
    
class AgregarPedido2View(TemplateView):                                                  # Agrega pedidos - paso 2
    template_name = 'agregarPedido2.html'

    def get(self, request, *args, **kwargs):
        mensajes = request.session.get('mensajes', None)
        cliente = request.session.get('idCliente', None)
        idCliente = Cliente.objects.get(id=cliente)
        direcciones = Direcciones.objects.filter(idCliente=cliente)
        metodospago = MetodoPago.objects.all().order_by('id')
        context ={
            'title': 'Crear pedido',
            'subtitle': 'Seleccionar los datos de despacho',
            'form': FormularioCrearPedidos(),
            'mensajes': mensajes,
            'cliente': cliente,
            'buscaCliente': idCliente,
            'direcciones': direcciones,
            'metodospago': metodospago,
        }
        return render(request,self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = FormularioCrearPedidos(request.POST)
        if form.is_valid():
            registro = Pedidos(
                idCliente = form.cleaned_data['idCliente'],
                idDireccion = form.cleaned_data['idDireccion'],
                instrucciones_entrega = form.cleaned_data['instrucciones_entrega'],
                idUsuario = CustomUser.objects.get(id=request.user.id),
                idEstado = Estado_Pedido.objects.get(id=1),
                idMetodoPago = form.cleaned_data['idMetodoPago'],
            )
            registro.save()
            request.session['mensajes'] = {'enviado': True, 'resultado': 'Se ha creado el pedido exitosamente, ahora puedes llenar el pedido con los productos de la plataforma'}
            return redirect('agregarpedidopaso3')
        else:
            mensajes = {'enviado': False, 'resultado': form.errors}

        context = {
            'form': form,
            'mensajes': mensajes,
            }
        return render(request, self.template_name, context)
    
class AgregarPedido3View(TemplateView):                                                 # Agrega pedidos - paso 3
    template_name = 'agregarPedido3.html'

    def get(self, request, *args, **kwargs):
        last_pedido = Pedidos.objects.filter(idUsuario=request.user).latest('id')
        context ={
            'title': 'Crear pedido',
            'subtitle': 'Completar el pedido',
            'last_pedido': last_pedido,
            'form': FormularioCrearDetalle(),
            'detalle_pedido': Detalles_Pedido.objects.filter(idPedidos=last_pedido).annotate(total=F('cantidad') * F('precio')),
            'total_pedido': Detalles_Pedido.objects.filter(idPedidos=last_pedido).aggregate(total=Sum(F('cantidad') * F('precio')))['total'],
            'mensajes' : request.session.get('mensajes', None),
        }
        request.session.pop('mensajes', None)
        request.session.pop('idEmpresa', None)
        return render(request,self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = FormularioCrearDetalle(request.POST)
        if form.is_valid():
            producto = form.cleaned_data.get('idProductos')
            registro = Detalles_Pedido(
                cantidad = form.cleaned_data['cantidad'],
                idPedidos = Pedidos.objects.filter(idUsuario=request.user).latest('id'),
                idProductos = form.cleaned_data['idProductos'],
                precio = Productos.objects.get(nombre=producto).precio,
            )
            registro.save()
            request.session['mensajes'] = {'enviado': True, 'resultado': f'Se ha agregado {producto} al pedido exitosamente'}
            return redirect('agregarPedido3')
        else:
            mensajes = {'enviado': False, 'resultado': form.errors}

        context = {
            'form': form
        }
        return render(request, self.template_name, context)

class ActualizarEstadoPedidoView(TemplateView):                                                 # Actualiza el estado de los pedidos
    template_name = 'actualizar_estado.html'
    
    def get(self, request, *args, **kwargs):
        idpedido = kwargs['idpedido']
        try:
            pedido = Pedidos.objects.get(id=idpedido)
        except Pedidos.DoesNotExist:
            return render(request, 'elemento_no_existe.html')
        pedido = Pedidos.objects.get(id=idpedido)
        email_cliente =  CustomUser.objects.get(id=pedido.idUsuario_id).email
        grupo_cliente = CustomUser.objects.get(id=pedido.idUsuario_id).groups.first().id
        grupo_usuario = request.user.groups.first().id
        context = {
            'form': FormularioActualizarEstado(instance=pedido),
            'idpedido': idpedido,
            'pedido': pedido,
            'title': f'Modificar el estado del pedido {idpedido}',
            'email_cliente': email_cliente,
            'grupo_cliente': grupo_cliente,
            'grupo_usuario': grupo_usuario,
        }
        
        request.session['email_cliente'] = email_cliente
        request.session['grupo_cliente'] = grupo_cliente
        request.session['grupo_usuario'] = grupo_usuario
        return render(request, self.template_name, context)

    def post(self, request, idpedido, *args, **kwargs):             
        instance = get_object_or_404(Pedidos, id=self.kwargs['idpedido'])
        form = FormularioActualizarEstado(request.POST, instance=instance)
        reenvio = reverse('detalle_pedido', kwargs={'idpedido': idpedido})
        pedido = self.kwargs['idpedido']
        email_cliente = request.session['email_cliente']
        grupo_cliente = request.session['grupo_cliente']
        request.session.pop('email_cliente', None)
        request.session.pop('grupo_cliente', None)
        if form.is_valid():
            form.save()
            request.session['mensajes'] = {'enviado': True, 'resultado': 'Se ha actualizado el estado del pedido'}
            estado = Pedidos.objects.get(id=pedido).idEstado
            if grupo_cliente == 1:
                mensaje = f'''
                    Cambio de estado de pedido.
                    El estado del pedido {pedido} ha cambiado, y su nuevo estado es {estado}
                    En caso de dudas, puede contactanos para revisar nuevamente su pedido.


                    Muchas Gracias por su preferencia
                '''
                send_mail(
                    f'[TeLoEnvio] - Cambio de estado de pedido número {pedido}',
                    mensaje,
                    os.environ.get('EMAIL_HOST_USER'),  # Usar el correo configurado en settings.py
                    [email_cliente],  # Enviar el correo al destinatario ingresado por el usuario
                    fail_silently=False
                )
                request.session['mensajes'] = {'enviado': True, 'resultado': 'Se ha actualizado el estado del pedido y envíado un email al cliente'}
            return redirect(reenvio)
        return self.render_to_response(self.get_context_data())


class VistaDetallesView(TemplateView):                                                    # Listado de detalles de un pedido
    template_name = 'detallesPedidos.html'
    def get(self, request, idpedido, *args, **kwargs):
        try:
            pedido = Pedidos.objects.get(id=idpedido)
        except Pedidos.DoesNotExist:
            return render(request, 'elemento_no_existe.html')
        context ={
            'title': f'Detalle de orden {pedido}',
            'pedido': pedido,
            'cliente': Cliente.objects.get(id=pedido.idCliente_id),
            'direccion': Direcciones.objects.get(id=pedido.idDireccion_id),
            'detalle_pedido': Detalles_Pedido.objects.filter(idPedidos=idpedido).annotate(total=F('cantidad') * F('precio')),
            'usuario': CustomUser.objects.get(id=pedido.idUsuario_id),
            'grupo_usuario_actual': request.user.groups.first().id,
            'total_pedido': Detalles_Pedido.objects.filter(idPedidos=idpedido).aggregate(total=Sum(F('cantidad') * F('precio')))['total'],
            'mensajes' : request.session.get('mensajes', None),
            }
        request.session.pop('mensajes', None)
        return render(request, self.template_name, context)
    
class FinalizarPedidoView(TemplateView):                                                       # Agrega pedidos - cierre del pedido
    template_name = 'finalizarPedido.html'

    def get(self, request, *args, **kwargs):
        request.session.pop('mensajes', None)
        request.session.pop('idCliente', None)

        context = {
            'title': '🎉 El pedido está finalizado',
        }

        return render(request, self.template_name, context)