#!/bin/sh
set -e
envsubst '$DJANGO_SERVER_NAME' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf
exec nginx -g 'daemon off;' 