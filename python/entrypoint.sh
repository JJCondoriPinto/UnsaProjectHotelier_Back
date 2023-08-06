#!/bin/sh

# Aplicar migraciones
python manage.py migrate

echo "from Apis.models import User; User.objects.create_superuser('${DJANGO_SU_EMAIL}', '${DJANGO_SU_PASSWORD}', nombres='${DJANGO_SU_NOMBRES}', apellidos='${DJANGO_SU_APELLIDOS}', dni='${DJANGO_SU_DNI}', telefono='${DJANGO_SU_TELEFONO}')" | python manage.py shell

# Iniciar el servicio de Nginx
service nginx start

# Ejecutar Gunicorn
gunicorn FastBooking.wsgi:application --bind 0.0.0.0:8000
