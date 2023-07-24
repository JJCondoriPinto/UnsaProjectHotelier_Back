from django.urls import path
from .views import *

urlpatterns = [
    path('habitaciones/', HabitacionesApiView.as_view(), name='habitaciones'),
    path('habitaciones/<int:id>', HabitacionesApiView.as_view(), name='habitaciones-one'),
    path('recepcionistas/', RecepcionistasApiView.as_view(), name='recepcionistas'),
    path('recepcionistas/<int:id>', RecepcionistasApiView.as_view(), name='recepcionistas-one'),
    path('huespedes/', HuespedesApiView.as_view(), name='huespedes'),
    path('huespedes/<int:id>', HuespedesApiView.as_view(), name='huespedes-one'),
    path('acompanantes/<int:idTitular>', AcompanantesApiView.as_view(), name='acompanantes'),
    path('acompanantes/<int:idTitular>/<int:id>', AcompanantesApiView.as_view(), name='acompanantes-one'),
]