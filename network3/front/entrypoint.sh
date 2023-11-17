#!/bin/sh

django_ip=$(getent hosts django3 | awk '{ print $1 }')

export DJANGO_BASE_URL=http://$django_ip:5000

env

npm run dev

exec "$@"