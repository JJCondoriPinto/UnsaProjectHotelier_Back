from rest_framework import routers
from .views import *

router = routers.DefaultRouter()

router.register('recepcionistas', RecepcionistasViewSet, 'recepcionistas')
router.register('habitaciones', HabitacionesViewSet, 'habitaciones')

urlpatterns = router.urls