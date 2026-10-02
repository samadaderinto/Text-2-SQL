FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY server/requirements.txt ./
RUN apk add --no-cache mariadb-connector-c \
    && apk add --no-cache --virtual .build-deps build-base mariadb-connector-c-dev pkgconf
RUN pip install --no-cache-dir --retries 5 --timeout 60 -r requirements.txt
RUN apk del .build-deps

COPY server/ .

EXPOSE 10000

CMD ["sh", "-c", "python manage.py migrate && (python manage.py create_prod_admin || true) && python manage.py collectstatic --noinput && exec gunicorn server.wsgi:application --bind 0.0.0.0:${PORT:-10000}"]
