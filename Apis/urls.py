from django.urls import path
from .views import *

urlpatterns = [

    path('auth/', AuthenticateApiView.as_view()),

    path('habitaciones/', HabitacionesApiView.as_view(), name='habitaciones'),
    path('habitaciones/<int:id>', HabitacionesApiView.as_view(), name='habitaciones-one'),

    path('recepcionistas/', RecepcionistasApiView.as_view(), name='recepcionistas'),
    path('recepcionistas/<int:id>', RecepcionistasApiView.as_view(), 
    name='recepcionistas-one'),

    path('huespedes/', HuespedesApiView.as_view(), name='huespedes'),
    path('huespedes/<int:id>', HuespedesApiView.as_view(), name='huespedes-one'),

    path('acompanantes/<int:idTitular>', AcompanantesApiView.as_view(), name='acompanantes'),
    path('acompanantes/<int:idTitular>/<int:id>', AcompanantesApiView.as_view(), name='acompanantes-one'),

    path('reservas/', ReservasApiView.as_view(), name='reservas'),
    path('reservas/<int:id>', ReservasApiView.as_view(), name='reservas-one'),

    path('checkins/', CheckinsApiView.as_view(), name='checkins'),
    path('checkins/<int:id>', CheckinsApiView.as_view(), name='checkins-one'),

    path('checkouts/', CheckoutApiView.as_view(), name='checkouts'),
    path('checkouts/<int:id>', CheckoutApiView.as_view(), name='checkouts-one'),

    path('reminds/', RemindApiView.as_view(), name='reminds'),
    path('reminds/<int:id>', RemindApiView.as_view(), name='reminds-one'),

    path('reports/', ReportApiView.as_view(), name='reports')

]