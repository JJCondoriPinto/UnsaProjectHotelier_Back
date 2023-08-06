# Django Backend

Para ejecutar la aplicación con Docker, primero debemos de crear la base de datos, seguido deL proyecto de Django, para ello seguimos los siguientes pasos:

## Mysql:

1. Crear un contenedor de mysql, para ello primero deberás de construir la imagen a partir del Dockerfile, ubícate en el directorio 'mysql':

    ```
    cd ./mysql
    ```

2. Construir la imagen de mysql:

    ```
    docker build -t mysql_pweb .
    ```

## Django:

1. Para crear la imagen de django seguiremos los mismos pasos que para el contenedor de mysql:

    ```
    cd ./python
    docker build -t django_pweb .
    ```

## Conexion de red:

Por defecto, cuando creemos los contenedores estos estarán separados y no tendrán comunicación, para ello podemos crear un docker-compose e implementar ambos contenedores como servicios, sin embargo, usaremos otro comando:

```
docker network create web
```

Donde 'web' será el nombre de nuestra red, siendo útil para comunicar los contenedores de mysql y django.

Luego de crear la red podemos iniciar los contenedores, sin embargo, para evitar la pérdida de información se opta por crear volúmenes, para ello, utilizamos la opción '-v':

```
docker run -d -p 3306:3306 --name db --network web -v db_pweb_volume:/var/lib/mysql mysql_pweb
docker run -d -p 80:80 --name django --network web -v django_pweb_volume:/usr/src/app django_pweb
```

Esperamos a que el contenedor de mysql termine de iniciar y acepte conexiones, luego de ello creamos el contenedor de django, si lo ejecutó antes puede reiniciarlo hasta que la base de datos esté disponible.
