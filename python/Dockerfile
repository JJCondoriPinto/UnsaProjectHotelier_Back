FROM python:3.11.4-slim-buster

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config nginx \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app
COPY . .

COPY nginx/app_nginx.conf /etc/nginx/sites-available/default

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

RUN chmod +x entrypoint.sh

EXPOSE 80

ENTRYPOINT [ "./entrypoint.sh" ]