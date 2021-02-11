#!/bin/bash

# start Django
cd uks
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
# python uks/manage.py runserver 0.0.0.0:8000
gunicorn uks.wsgi -b 0.0.0.0:8000
