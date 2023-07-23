from django.http import JsonResponse

from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .models import *

import json


# Vista AuthToken sobreescrita para validación sobre Token custom
class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'nombres': user.nombres,
            'apellidos': user.apellidos,
            'turno': user.turno,
            'rol': user.rol
        })


# Apis de consumo (Gerente)
class HabitacionesApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, id=None, *args, **kargs):
        if id is not None:
            habitacion = Habitacion.objects.get(pk=id)
            serializerHabit = HabitacionSerializer(habitacion)
            serializerConte = ContenidoSerializer(habitacion.contenido_set.all(), many=True)
            finalData = serializerHabit.data.copy()
            finalData['contenido'] = serializerConte.data.copy()
            return Response(finalData)
        else:
            habitaciones = Habitacion.objects.all()
            serializer = HabitacionSerializer(habitaciones, many=True)
            return Response(serializer.data)

    def post(self, request, *args, **kargs):
        # Validación general
        data = request.data
        serializer = HabitacionSerializer(data=data)
        if serializer.is_valid():
            habitacion = serializer.create(data)

            # Validación e inserción para contenido de habitación
            if 'contenido' in data:
                for contenido in data['contenido']:
                    serializer_content = ContenidoSerializer(data=contenido)
                    contenido['habitacion_id'] = habitacion.pk
                    if serializer_content.is_valid():
                        serializer_content.create(contenido)

            
            return JsonResponse(data={
                "message":"Habitación creada correctamente",
                "id": habitacion.pk
            })
        else:
            return Response(serializer.errors, status=409)
    
    def patch(self, request, id, *args, **kargs):
        habitacion = Habitacion.objects.get(pk=id)
        habitacion.imagen = request.data['image']
        habitacion.save()
        return Response(status=204)

    def put(self, request, id, *args, **kargs):
        # Validación general
        data = request.data
        habitacion = Habitacion.objects.get(pk=id)
        serializer = HabitacionSerializer(instance=habitacion, data=data)

        if serializer.is_valid():
            habitacion = serializer.update(instance=habitacion, validated_data=data)

            # Validación e inserción para contenido de habitación
            if 'contenido' in data:
                habitacion.contenido_set.all().delete() # Actualiza contenido
                for contenido in data['contenido']:
                    serializer_content = ContenidoSerializer(data=contenido)
                    contenido['habitacion_id'] = habitacion.pk
                    if serializer_content.is_valid():
                        serializer_content.create(contenido)

            
            return JsonResponse(data={
                "message":"Habitación actualizada correctamente",
                "id": habitacion.pk
            })
        else:
            return Response(serializer.errors, status=409)

    def delete(self, request, id, *args, **kargs):
        try:
            Habitacion.objects.get(pk=id).delete()
            return JsonResponse(data={
                "message":"Habitación eliminada"
            })
        except Exception:
            return JsonResponse(data={
                "message":"Error en la eliminación"
            })


class RecepcionistasApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, id=None, *args, **kargs):
        if id is not None:
            try:
                recepcionista = User.objects.get(pk=id, rol='recepcionista')
                serializer = UserSerializer(recepcionista)
                return Response(serializer.data)
            except Exception:
                return JsonResponse({"message":"Recepcionista no encontrado"})
        else:
            recepcionistas = User.objects.filter(rol='recepcionista')
            serializer = UserSerializer(recepcionistas, many=True)
            return Response(serializer.data)

    def post(self, request, *args, **kargs):
        # Validación general
        data = request.data
        serializer = UserSerializer(data=data)
        validPassword = data['password'] == data['confirmPassword']
        if serializer.is_valid() and validPassword:
            del data['confirmPassword']
            serializer.create_user(data)
            return JsonResponse(data={
                "message":"Recepcionista registrado correctamente"
            })
        else:
            errors = serializer.errors.copy()
            if not validPassword:
                errors.setdefault('password', []).append('Contraseñas no coinciden')
            return Response(errors, status=409)
            

    def put(self, request, id, *args, **kargs):
        # Validación general
        data = request.data
        recepcionista = User.objects.get(pk=id)
        serializer = UserSerializer(instance=recepcionista, data=data)
        validPassword = data['password'] == data['confirmPassword']
        if serializer.is_valid():
            del data['confirmPassword']
            if data['password'] != '':  # Se actualiza la contraseña
                serializer.update_user_password(data, id)
            del data['password']
            serializer.update(recepcionista, data)
            return JsonResponse(data={
                "message":"Recepcionista actualizado correctamente"
            })
        else:
            errors = serializer.errors.copy()
            if not validPassword:
                errors.setdefault('password', []).append('Contraseñas no coinciden')
            return Response(errors, status=409)

    def delete(self, request, id, *args, **kargs):
        try:
            User.objects.get(pk=id).delete()
            return JsonResponse(data={
                "message":"Recepcionista eliminado"
            })
        except Exception:
            return JsonResponse(data={
                "message":"Error en la eliminación"
            })

# Apis para consumo simple (Recepcionista)
