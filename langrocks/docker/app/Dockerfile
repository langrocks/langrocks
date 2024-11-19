FROM nginx:stable-alpine3.20-slim

RUN rm /etc/nginx/conf.d/default.conf
ADD langrocks/docker/app/nginx.conf /etc/nginx/conf.d

COPY langrocks/app/web/dist /usr/share/nginx/html

EXPOSE 80