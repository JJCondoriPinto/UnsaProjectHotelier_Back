#!/bin/bash

echo "Entrypoint django"

ls
pwd
ls -al

exec gunicorn FastBooking.wsgi:application --bind 0.0.0.0:8000