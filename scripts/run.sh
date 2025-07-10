#!/bin/sh

set -e
#python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.asgi:application --bind 0.0.0.0:8000
