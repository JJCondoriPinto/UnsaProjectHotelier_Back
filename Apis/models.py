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
    dni = models.CharField(max_length=8, unique=True)
    telefono = models.CharField(max_length=9)
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
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'administrador'
        verbose_name_plural = 'administradores'
    
    def get_full_name(self):
        return self.nombres
    
    def get_short_name(self):
        return self.nombres or self.email.split('@')[0]