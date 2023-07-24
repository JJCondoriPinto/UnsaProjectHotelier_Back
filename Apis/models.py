from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone

# Create your models here.
class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Debes proporcionar un email valido")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'gerente')
        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    roles = [
        ('recepcionista', 'recepcionista'),
        ('gerente', 'gerente')
    ]
    turnos = [
        ('mañana', 'mañana'),
        ('tarde', 'tarde'),
        ('noche', 'noche'),
        ('finesSemana', 'finesSemana'),
    ]

    email = models.EmailField(blank=True, default='', unique=True)
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    dni = models.PositiveIntegerField(unique=True)
    telefono = models.PositiveIntegerField(unique=True)
    rol = models.CharField(max_length=15, choices=roles, default='recepcionista')
    turno = models.CharField(max_length=15, choices=turnos)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['nombres', 'apellidos', 'dni', 'telefono']
    
    class Meta:
        db_table = 'administradores'
        verbose_name = 'administrador'
        verbose_name_plural = 'administradores'
    
    def get_full_name(self):
        return self.nombres
    
    def get_short_name(self):
        return self.nombres or self.email.split('@')[0]

# Modelos para consumo en hotel
class Habitacion(models.Model):

    estados = [
        ('Libre', 'Libre'),
        ('Ocupado', 'Ocupado'),
        ('Reservado', 'Reservado'),
        ('Limpieza', 'Limpieza'),
        ('No operativo', 'NoOperativo'),
    ]

    nro_habitacion = models.PositiveIntegerField(unique=True, null=False)
    nro_piso = models.PositiveSmallIntegerField(null=False)
    tipo_habitacion = models.CharField(null=False, max_length=30)
    precio = models.DecimalField(max_digits=6, decimal_places=2, null=False)
    estado = models.CharField(choices=estados, default='Libre', max_length=12)
    tamanio = models.DecimalField(max_digits=4, decimal_places=2)
    imagen = models.ImageField(upload_to='habitaciones', null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=False)

class Contenido(models.Model):
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE, null=False)
    nombre = models.CharField(max_length=100, null=False)
    cantidad = models.PositiveIntegerField(default=1, null=False)
    descripcion = models.CharField(max_length=100, null=True)

class Huesped(models.Model):
    tipos_identificacion = [
        ('Dni', 'Dni'),
        ('Carnet_Extranjeria', "Carnet_Extranjeria")
    ]

    tipo_identificacion = models.CharField(max_length=20, choices=tipos_identificacion)
    identificacion = models.CharField(max_length=20, null=False, unique=True)

    nombres = models.CharField(max_length=50, null=False)
    apellidos = models.CharField(max_length=50, null=False)
    sexo = models.CharField(choices=[('Masculino', 'masculino'), ('Femenino', 'femenino')], null=False, max_length=9)
    fecha_nacimiento = models.DateField(auto_created=False)

    nacionalidad = models.CharField(max_length=20, null=False)
    region = models.CharField(max_length=30)
    telefono = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True, null=False,)

    # Opcional, si el huesped viaja por motivos de negocio
    ruc_empresa = models.CharField(null=True, max_length=11)

class Acompanante(models.Model):
    titular = models.ForeignKey(Huesped, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    sexo = models.CharField(choices=[('Masculino', 'masculino'), ('Femenino', 'femenino')], null=False, max_length=9)

    tipo_identificacion = models.CharField(max_length=20, null=True)
    identificacion = models.CharField(max_length=20, null=True, unique=True)

    relacion = models.CharField(max_length=50, help_text="Relación con el titular")

class Reserva(models.Model):

    estados = [
        ('Pendiente', 'pendiente'), # Aún ho hay checkin
        ('Cancelado', 'cancelado'), 
        ('Pasado', 'pasado'),  # No llegó el huesped
        ('Registrado', 'Registrado') # Cuando se realizó el checkin
    ]

    # Para saber cuál recepcionista lo realizó
    recepcionista = models.ForeignKey(User, on_delete=models.SET_NULL, name='recepcionista', null=True)

    titular = models.ForeignKey(Huesped, on_delete=models.CASCADE)
    cantidad_dias = models.PositiveIntegerField(null=False)
    tipo_reserva = models.CharField(choices=[('Presencial', 'presencial'), ('Virtual', 'virtual')], default='presencial', max_length=15)
    razon_hospedaje = models.CharField(max_length=50)
    peticiones = models.TextField(max_length=100)
    fecha_llegada = models.DateTimeField(null=False)
    estado = models.CharField(choices=estados, default='Pendiente', max_length=10)

    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True, null=False,)

class Checkin(models.Model):

    estados = [
        ('Activo', 'activo'), # Checkin vigente
        ('Inactivo', 'inactivo') # Checkout realizado
    ]
    
    # Para saber cuál recepcionista lo realizó
    recepcionista = models.ForeignKey(User, on_delete=models.SET_NULL, name='recepcionista', null=True)

    reserva = models.OneToOneField(Reserva,on_delete=models.CASCADE)
    fecha_entrada = models.DateTimeField(auto_now_add=True, null=False)
    estado = models.CharField(choices=estados, default='Activo', max_length=8)

    paxx = models.PositiveIntegerField(default=0) # Número de acompañantes

class Checkout(models.Model):

    # Para saber cuál recepcionista lo realizó
    recepcionista = models.ForeignKey(User, on_delete=models.SET_NULL, name='recepcionista', null=True)

    checkin = models.OneToOneField(Checkin, on_delete=models.CASCADE)
    fecha_salida = models.DateTimeField(auto_now_add=True, null=False)
    descripcion_salida = models.CharField(blank=True, null=True, max_length=500)
