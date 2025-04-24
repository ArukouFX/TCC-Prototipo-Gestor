#!/bin/sh
# Ejecuta migraciones y luego inicia Gunicorn
python manage.py makemigrations --noinput
python manage.py migrate --noinput
gunicorn --bind 0.0.0.0:8000 --timeout 3600 utec_scheduler.wsgi:application
