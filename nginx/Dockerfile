FROM nginx:latest
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./nginx/nginx_proxy.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]