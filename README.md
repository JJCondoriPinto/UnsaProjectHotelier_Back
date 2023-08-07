# Django Backend

Para ejecutar la aplicación con Docker, primero debemos de crear la base de datos, seguido deL proyecto de Django, para ello seguimos los siguientes pasos:

## Requirements:

-   asgiref
-   packaging
-   Django -> El framework base (importante)
-   django-cors-headers -> Permite conexión desde otros servidores (importante)
-   djangorestframework -> Para la elaboración de apis (importante)
-   gunicorn -> Servidor basado en wsgi (importante)
-   mysqlclient -> Permite conexión con Mysql
-   Pillow -> Procesamiento de imágenes
-   pytz -> Manejo de zonas horarias
-   sqlparse -> Formato de sentencias SQL
-   tzdata -> Manejo de zona horaria

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
docker run -d -p 8000:80 --name django --network web -v django_pweb_volume:/usr/src/app django_pweb
```

Esperamos a que el contenedor de mysql termine de iniciar y acepte conexiones, luego de ello creamos el contenedor de django, si lo ejecutó antes puede reiniciarlo hasta que la base de datos esté disponible.


## Ejecución local:

Si no se desea crear un contenedor de Docker, el proyecto puede ser iniciado de manera local, para ello se deben tomar en cuenta las siguientes consideraciones:

-   La base de datos puede mantenerse, en caso se haya creado el contenedor de mysql, solo se tendría que modificar el host a localhost y en el puerto 3306, si no se creó con anterioridad entonces en `settings.py` se deben de colocar los datos de la base de datos local.

-   En caso se haga uso del servidor de nginx, puede ser utilizado el archivo `app_nginx.conv` dentro del directorio `python/nginx`, con la diferencia de que el servidor de backend debería escuchar al host localhost y en el mismo puerto 8000, caso contrario, puede utilizar el servidor de wsgi de django: `python manage.py runserver`

-   Las migraciones se ejecutarían de forma manual, al igual que la creación del superusuario.

-   Para la conexión con el Front End de Angular, será necesario modificar el CORS en `settings.py`, autorizando a localhost y el puerto por defecto de Angular, sea 4200 o, si se utiliza su servidor de nginx, sería en el puerto 80