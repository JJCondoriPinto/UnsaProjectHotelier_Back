FROM python:3.11.4-slim-buster

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app
COPY . .

COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
# CMD ["gunicorn", "FastBooking.wsgi:application", "--bind 0.0.0.0:8000"]