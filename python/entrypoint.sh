#!/bin/bash

ls

echo "Entrypoint django"

exec gunicorn FastBooking.wsgi:application --bind 0.0.0.0:8000