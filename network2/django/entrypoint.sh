#!/bin/sh




yes | python manage.py makemigrations > /dev/stderr
yes | python manage.py makemigrations api > /dev/stderr
yes yes | python manage.py migrate > /dev/stderr


python scripts/producer.py &
python scripts/consumer.py &
python manage.py runserver 0.0.0.0:5000 > /dev/stderr

