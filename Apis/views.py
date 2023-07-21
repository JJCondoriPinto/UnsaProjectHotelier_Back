from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .serializers import *
from .models import *


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


# Apis de consumo simple
class HabitacionesViewSet(viewsets.ModelViewSet):
    queryset = Habitacion.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = HabitacionSerializer

class RecepcionistasViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(rol='recepcionista')
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer