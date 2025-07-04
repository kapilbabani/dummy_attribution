# To generate self-signed certs for Nginx, run:
# mkdir -p nginx/certs
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/certs/server.key -out nginx/certs/server.crt -subj "/CN=localhost" 

server {
    listen ${NGINX_PORT} ssl;
    server_name ${DJANGO_SERVER_NAME};

    ssl_certificate /etc/nginx/certs/server.crt;
    ssl_certificate_key /etc/nginx/certs/server.key;

    location /static/ {
        alias /static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location / {
        proxy_pass http://web:${DJANGO_RUNSERVER_PORT};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
server {
    listen ${NGINX_HTTP_PORT};
    server_name ${DJANGO_SERVER_NAME};
    return 301 https://${DJANGO_SERVER_NAME}$request_uri;
} 