FROM python:3

WORKDIR /var/www/server
RUN pip3 install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy
COPY . .

