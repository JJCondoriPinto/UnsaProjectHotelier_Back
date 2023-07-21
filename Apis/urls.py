from django.urls import path
from .views import *

urlpatterns = [
    path('habitaciones/', HabitacionesApiView.as_view(), name='habitaciones'),
    path('habitaciones/<int:id>', HabitacionesApiView.as_view(), name='habitaciones-one'),
    path('recepcionistas/', RecepcionistasApiView.as_view(), name='recepcionistas'),
    path('recepcionistas/<int:id>', RecepcionistasApiView.as_view(), name='recepcionistas-one'),
]