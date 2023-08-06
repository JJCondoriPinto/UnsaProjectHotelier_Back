FROM mysql:8.0

# Establece las variables de entorno para configurar la base de datos
ENV MYSQL_ROOT_PASSWORD=root
ENV MYSQL_DATABASE=fastbooking
ENV MYSQL_USER=fastbook
ENV MYSQL_PASSWORD=gWqzP0up6FYm3P2cUfQRWmkM

COPY ./sql /docker-entrypoint-initdb.d

EXPOSE 3306

CMD ["mysqld", "--character-set-server=utf8mb4", "--collation-server=utf8mb4_unicode_ci", "--default-authentication-plugin=mysql_native_password"]
