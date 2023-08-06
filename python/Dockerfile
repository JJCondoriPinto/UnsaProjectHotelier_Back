FROM python:3.11.4-slim-buster

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app
COPY . .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

CMD ["gunicorn", "FastBooking.wsgi:application", "--bind", "0.0.0.0:8000"]