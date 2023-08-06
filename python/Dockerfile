FROM python:3.11.4-slim-buster

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config nginx \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Variables de entorno para el superusuario
ENV DJANGO_SU_EMAIL="fastbook@fastbooking.com"
ENV DJANGO_SU_PASSWORD="7Cu8TL4KpFS3tturZqT5bphc"
ENV DJANGO_SU_DNI="11111111"
ENV DJANGO_SU_TELEFONO="999999999"
ENV DJANGO_SU_NOMBRES="Gerente"
ENV DJANGO_SU_APELLIDOS="Gerente"

WORKDIR /usr/src/app

COPY . .
COPY nginx/app_nginx.conf /etc/nginx/sites-available/default

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY entrypoint.sh /usr/src/app/
RUN chmod +x entrypoint.sh

EXPOSE 80
ENTRYPOINT [ "./entrypoint.sh" ]