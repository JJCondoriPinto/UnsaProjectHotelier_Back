FROM python:3.11.3-slim-bullseye

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY . .

RUN pip install --upgrade pip \
    && pip install mysqlclient \
    && pip install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]