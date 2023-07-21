from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import *

# Token customizado para validación de email
class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'nombres', 'apellidos',  'dni', 'telefono', 'turno', 'email')
        read_only_fields = ['rol']

    def create_user(self, validated_data):
        return User.objects.create_user(**validated_data)

class HabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitacion
        fields = ('id', 'nro_habitacion', 'nro_piso', 'tipo_habitacion', 'precio', 'estado', 'tamanio', 'imagen')
        read_only_fields = ['created_at']

class ContenidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contenido
        fields = ('id', 'habitacion_id', 'nombre', 'cantidad', 'descripcion')
    
class HuespedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Huesped
        fields = ('id', 'tipo_identificacion', 'identificacion', 'nombres', 'apellidos', 'sexo', 'fecha_nacimiento', 'nacionalidad', 'region', 'telefono', 'ruc_empresa')
        read_only_fields = ['created_at']

class AcompananteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acompanante
        fields = ('id', 'titular_id', 'nombres', 'apellidos', 'sexo', 'tipo_identificacion', 'identificacion', 'relacion')

class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = ('id', 'recepcionista_id', 'titular_id', 'cantidad_dias', 'tipo_reserva', 'razon_hospedaje', 'fecha_llegada', 'relacion', 'estado', 'habitacion_id')
        read_only_fields = ['created_at']

class CheckinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkin
        fields = ('id', 'recepcionista_id', 'reserva_id', 'fecha_entrada', 'estado', 'paxx')

class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkout
        fields = ('id', 'recepcionista_id', 'checkin_id', 'fecha_salida', 'descripcion_salida')