from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token
from .models import Employee
from rest_framework.response import Response
from .serializers import EmployeeSerializer, CustomAuthTokenSerializer

# Create your views here.
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all() # Consulta guardad en un set
    permission_classes = [permissions.IsAuthenticated] # Permisos para los objetos del modelo
    authentication_classes = [TokenAuthentication]
    serializer_class = EmployeeSerializer


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