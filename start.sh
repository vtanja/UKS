#!/bin/bash

# start Django
python uks/manage.py collectstatic --noinput
python uks/manage.py makemigrations
python uks/manage.py migrate
python uks/manage.py runserver 0.0.0.0:8000
#gunicorn uks.uks.wsgi -b 0.0.0.0:8000
