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
        if 'imagen' in request.data:
            habitacion.imagen = request.data['image']
        if 'estado' in request.data:
            habitacion.estado = request.data['estado']
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
class HuespedesApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, id=None, *args, **kargs):

        if id is not None:
            huesped = Huesped.objects.get(pk=id)
            serializer = HuespedSerializer(instance=huesped)
            return Response(serializer.data)
        else:
            huespedes = Huesped.objects.all()
            serializer = HuespedSerializer(huespedes, many=True)
            return Response(serializer.data)
    
    def post(self, request, *args, **kargs):

        data = request.data
        serializer = HuespedSerializer(data=data)
        if serializer.is_valid():
            serializer.create(validated_data=data)
            return Response(status=204)
        else:
            return Response(serializer.errors, status=409)
    
    def delete(self, id, *args, **kargs):
        
        try:

            Huesped.objects.get(pk=id).delete()
            return Response(status=204)

        except Exception:

            return Response("Error en la eliminación", status=409)
    
    def put(self, request, id, *args, **kargs):
        data = request.data
        huesped = Huesped.objects.get(pk=id)
        serializer = HuespedSerializer(instance=huesped, data=data)
        if serializer.is_valid():
            serializer.update(instance=huesped, validated_data=data)
            return Response("Huesped actualizado satisfactoriamente" ,status=200)
        else:
            return Response(status=409)

class AcompanantesApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, idTitular, id=None, *args, **kargs):
        if id is not None:
            try:
                acompanante = Acompanante.objects.get(pk=id, titular_id=idTitular)
                serializer = AcompananteSerializer(instance=acompanante)
                return Response(serializer.data)
            except Exception:
                return Response(status=404)
        else: 
            try:
                acompanante = Acompanante.objects.filter(titular_id=idTitular)
                serializer = AcompananteSerializer(instance=acompanante, many=True)
                return Response(serializer.data)
            except Exception:
                return Response(status=404)
            
    def post(self, request, idTitular, *args, **kargs):

        data = request.data
        serializer = AcompananteSerializer(data=data)
        if serializer.is_valid():
            serializer.create(validated_data=data)
            return Response(status=204)
        else:
            return Response(serializer.errors, status=409)

    def put(self, request, idTitular, id, *args, **kargs):
        data = request.data
        acompanante = Acompanante.objects.get(pk=id, titular_id=idTitular)
        serializer = AcompananteSerializer(instance=acompanante, data=data)
        if serializer.is_valid():
            serializer.update(instance=acompanante, validated_data=data)
            return Response("Acompañante actualizado satisfactoriamente", status=200)
        else:
            return Response(serializer.errors, status=409)

    def delete(self, request, idTitular, id, *args, **kargs):
        try:
            Acompanante.objects.get(pk=id, titular_id=idTitular).delete()
            return Response(status=204)
        except Exception:
            return Response("Error en la eliminacion", status=409)
