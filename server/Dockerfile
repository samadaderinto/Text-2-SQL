FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY server/requirements.txt ./
RUN apk add --no-cache mariadb-connector-c \
    && apk add --no-cache --virtual .build-deps build-base mariadb-connector-c-dev pkgconf \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

COPY server/ .

EXPOSE 10000

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && exec gunicorn server.wsgi:application --bind 0.0.0.0:${PORT:-10000}"]
