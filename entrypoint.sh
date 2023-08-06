#!/bin/bash

# Migraciones en caso la bd se inicialice por primera vez
# python manage.py migrate

# echo "from Apis.models import User; User.objects.create_superuser('fastbook@fastbooking.com', 'gWqzP0op6FYSWP2cUf0193mkM', nombres='Gerente', apellidos='Gerente', dni='222222', telefono='938201233')" | python manage.py shell

# Iniciar el servidor
service nginx start

gunicorn FastBooking.wsgi:application --bind 0.0.0.0:8000