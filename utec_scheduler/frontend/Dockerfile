FROM nginx:alpine

# Copiar archivos estáticos
COPY ./public /usr/share/nginx/html

# Copiar configuración de Nginx
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Exponer el puerto 8080
EXPOSE 8080

# Iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]