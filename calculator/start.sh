#!/bin/sh
# Fills $PORT into the nginx config, then starts nginx.
sed -e "s/\$PORT/${PORT:-8080}/g" /srv/nginx.conf > /tmp/nginx.conf
exec nginx -c /tmp/nginx.conf -g 'daemon off;'
