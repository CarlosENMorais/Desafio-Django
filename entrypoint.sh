#!/bin/sh

while ! nc -z $DB_HOST 5432; do
  sleep 0.1
done

python manage.py migrate --noinput
exec python manage.py runserver 0.0.0.0:8000
