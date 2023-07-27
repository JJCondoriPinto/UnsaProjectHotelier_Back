from django.http import JsonResponse
from django.core.exceptions import *

from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .models import *

from datetime import datetime, timedelta

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
            habitaciones = Habitacion.objects.all().exclude(**request.GET.dict())
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
        if habitacion.estado == 'NoOperativo':
            for reserva in habitacion.reserva_set.all():
                if reserva.estado == 'Pendiente':
                    reserva.estado = 'Cancelado'
                if reserva.estado == 'Registrado':
                    reserva.estado = 'Pasado'
                    checkout = Checkout()
                    checkout.checkin = reserva.checkin
                    checkout.recepcionista = request.user
                    checkout.save()
                    reserva.checkin.estado = 'Inactivo'
                    reserva.checkin.save()
                reserva.save()
        
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
            huesped = serializer.create(validated_data=data)
            return JsonResponse({
                'id': huesped.id,
                'status': 200
            })
        else:
            return Response(serializer.errors, status=409)
    
    def delete(self, request, id, *args, **kargs):
        
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
            return Response(serializer.errors, status=409)

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

class ReservasApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def getFechaLlegada(self, data_str):
        return datetime.strptime(data_str, "%Y-%m-%d").date()
        
    def getFechaSalida(self, fecha_llegada, cant_dias):
        return fecha_llegada + timedelta(days=cant_dias)

    def get(self, request, id=None, *args, **kargs):

        if id is not None:
            reserva = Reserva.objects.get(pk=id)
            serializer = ReservaSerializer(instance=reserva)
            return Response(serializer.data)
        else:
            reserva = Reserva.objects.all()
            serializer = ReservaSerializer(reserva, many=True)
            return Response(serializer.data)
    
    def post(self, request, *args, **kargs):

        data = request.data
        serializer = ReservaSerializer(data=data)
        if serializer.is_valid():

            habitacion = Habitacion.objects.get(pk=data['habitacion_id'])
            if habitacion.estado == 'NoOperativo':
                return Response("Habitacion no operativa", status=409)
            reservas = habitacion.reserva_set.filter(estado__in=['Pendiente', 'Registrado'])
            fecha_llegada = self.getFechaLlegada(data['fecha_llegada'])
            fecha_salida = self.getFechaSalida(fecha_llegada, data['cantidad_dias'])
            for reserva in reservas:
                entrada_reserva = reserva.fecha_llegada
                salida_reserva = self.getFechaSalida(reserva.fecha_llegada, reserva.cantidad_dias)
                if fecha_llegada >= salida_reserva or fecha_salida <= entrada_reserva:
                    continue # Fecha valida (no choca)
                errors = {}
                if fecha_llegada < salida_reserva and fecha_llegada >= entrada_reserva:
                    errors['fecha_llegada'] = f'Fecha de llegada invalida, puede ser mayor o igual a {salida_reserva}'
                elif fecha_salida > entrada_reserva and fecha_salida <= salida_reserva:
                    errors['cantidad_dias'] = f'Cantidad de dias invalido, una fecha limite es {entrada_reserva}'
                return Response(errors, status=409)

            reserva = serializer.create(validated_data=data)
            reserva.recepcionista_id = request.user.id
            reserva.save()
            habitacion.estado = 'Reservado'
            habitacion.save()
            return Response(status=204)
        else:
            return Response(serializer.errors, status=409)
    
    def delete(self, request, id, *args, **kargs):
        
        try:

            reserva = Reserva.objects.get(pk=id)
            habitacion = reserva.habitacion
            if habitacion.reserva_set.filter(estado='Pendiente').count() == 1:
                habitacion.estado = 'Libre'
                habitacion.save()

            return Response(status=204)

        except Exception:

            return Response("Error en la eliminación", status=409)
    
    def put(self, request, id, *args, **kargs):
        data = request.data
        reservaActual = Reserva.objects.get(pk=id)
        habitacionActual = reservaActual.habitacion # Habitacion actual reservada

        serializer = ReservaSerializer(instance=reservaActual, data=data)
        
        if serializer.is_valid():

            habitacion = Habitacion.objects.get(pk=data['habitacion_id']) # Habitacion a reservar

            if habitacion.estado == 'NoOperativo':
                return Response("Habitacion no operativa", status=409)
            
            reservas = habitacion.reserva_set.filter(estado='Pendiente')
            fecha_llegada = self.getFechaLlegada(data['fecha_llegada'])
            fecha_salida = self.getFechaSalida(fecha_llegada, data['cantidad_dias'])

            for reserva in reservas:
                entrada_reserva = reserva.fecha_llegada
                salida_reserva = self.getFechaSalida(reserva.fecha_llegada, reserva.cantidad_dias)
                if (fecha_llegada >= salida_reserva or fecha_salida <= entrada_reserva) or reserva == reservaActual:
                    continue # Fecha valida (no choca)
                errors = {}
                if fecha_llegada < salida_reserva and fecha_llegada >= entrada_reserva:
                    errors['fecha_llegada'] = f'Fecha de llegada invalida, puede ser mayor o igual a {salida_reserva}'
                if fecha_salida > entrada_reserva and fecha_salida <= salida_reserva:
                    errors['cantidad_dias'] = f'Cantidad de dias invalido, una fecha limite es {entrada_reserva}'
                return Response(errors, status=409)
            
            serializer.update(instance=reservaActual, validated_data=data)

            if habitacionActual != habitacion and habitacionActual.reserva_set.filter(estado='Pendiente').count() == 1:
                habitacionActual.estado = 'Libre'
                habitacionActual.save()

            habitacion.estado = 'Reservado'
            habitacion.save()
            return Response("Reserva actualizada satisfactoriamente" ,status=200)
        else:
            return Response(serializer.errors, status=409)

    def patch(self, request, id, *args, **kargs):

        data = request.data

        try:

            reservaActual = Reserva.objects.get(pk=id)

            if 'estado' in data:
                reservaActual.estado = data['estado']
            
            habitacion = reservaActual.habitacion
            if reservaActual.estado != 'Pendiente':
                if habitacion.reserva_set.filter(estado='Pendiente').count() == 1:
                    habitacion.estado = 'Libre'
                    habitacion.save()
            else:
                fecha_llegada = reservaActual.fecha_llegada
                fecha_salida = self.getFechaSalida(fecha_llegada, reservaActual.cantidad_dias)
                for reserva in habitacion.reserva_set.filter(estado='Pendiente'):
                    entrada_reserva = reserva.fecha_llegada
                    salida_reserva = self.getFechaSalida(reserva.fecha_llegada, reserva.cantidad_dias)
                    if (fecha_llegada >= salida_reserva or fecha_salida <= entrada_reserva) or reserva == reservaActual:
                        continue # Fecha valida (no choca)
                    if fecha_llegada < salida_reserva and fecha_llegada >= entrada_reserva or fecha_salida > entrada_reserva and fecha_salida <= salida_reserva:
                        return Response("La fecha de la reserva interfiere con otra ya existente", status=409)

            reservaActual.save()

            return Response(status=204)
        
        except Exception:

            return Response(status=400)

class CheckinsApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, id=None, *args, **kargs):
        if id is not None:
            reserva = Checkin.objects.get(pk=id)
            serializer = CheckinSerializer(instance=reserva)
            return Response(serializer.data)
        else:
            reserva = Checkin.objects.all()
            serializer = CheckinSerializer(reserva, many=True)
            return Response(serializer.data)

    def post(self, request, *args, **kargs):
        try:
            idReserva = request.data
            reserva = Reserva.objects.get(pk=idReserva)
            fecha_hoy = datetime.now().date()

            if reserva.fecha_llegada != fecha_hoy:
                return Response("Fecha de llegada no corresponde a la fecha actual", status=409)
            
            habitacion = reserva.habitacion
            huesped = reserva.titular
            paxx = huesped.acompanante_set.all().count()

            if habitacion.estado not in ['Reservado', 'Libre']:
                return Response("No se puede realizar el check in para esta habitacion por el momento", status=409)
            
            reserva.estado = 'Registrado'
            habitacion.estado = 'Ocupado'
            reserva.save()
            habitacion.save()

            checkin = Checkin()
            checkin.recepcionista = request.user
            checkin.paxx = paxx
            checkin.reserva = reserva
            checkin.save()

            return Response("Check in generado")
        
        except ObjectDoesNotExist:

            return Response(status=404)
        
        except Exception:

            return Response(status=400)


        
    def delete(self, request, id, *args, **kargs):

        try:

            checkin = Checkin.objects.get(pk=id)
    
            reserva = checkin.reserva
            reserva.estado = 'Pendiente'
            reserva.save()

            habitacion = reserva.habitacion
            habitacion.estado = 'Reservado'
            habitacion.save()

            checkin.delete()

            return Response(status=204)
        
        except ObjectDoesNotExist:

            return Response(status=404)
        
        except Exception:

            return Response(status=400)

class CheckoutApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, id=None, *args, **kargs):
        if id is not None:
            checkout = Checkout.objects.get(pk=id)
            serializer = CheckoutSerializer(instance=checkout)
            return Response(serializer.data)
        else:
            checkout = Checkout.objects.all()
            serializer = CheckoutSerializer(checkout, many=True)
            return Response(serializer.data)
        
    def post(self, request, *args, **kargs):
        try:
            data = request.data
            checkin = Checkin.objects.get(pk=data['checkin_id'])
            checkin.estado = 'Inactivo'
            checkin.save()

            reserva = checkin.reserva
            reserva.estado = 'Pasado'
            reserva.save()

            habitacion = reserva.habitacion
            habitacion.estado = 'Reservado' if habitacion.reserva_set.filter(estado='Pendiente').count() > 1 else 'Libre'
            habitacion.save()

            checkout = Checkout()
            checkout.recepcionista = request.user
            checkout.checkin = checkin
            tarifa = habitacion.precio * reserva.cantidad_dias
            checkout.tarifa = tarifa
            checkout.descripcion_salida = data['descripcion_salida']
            checkout.save()

            return Response("Check out generado")
        
        except ObjectDoesNotExist:

            return Response(status=404)
        
        except Exception:

            return Response(status=400)


        
    def delete(self, request, id, *args, **kargs):

        try:

            checkout = Checkout.objects.get(pk=id)

            checkin = checkout.checkin
            checkin.estado = 'Activo'
            reserva = checkin.reserva
            reserva.estado = 'Registrado'
            checkin.save()
            reserva.save()

            habitacion = reserva.habitacion
            habitacion.estado = 'Ocupado'
            habitacion.save()

            checkout.delete()

            return Response(status=204)
        
        except ObjectDoesNotExist:

            return Response(status=404)
        
        except Exception:

            return Response(status=400)

