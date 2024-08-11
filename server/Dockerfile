FROM python:3.12
WORKDIR /var/www/server
RUN pip3 install pipenv
ADD Pipfile /var/www/server
ADD Pipfile.lock /var/www/server
RUN python3 -m pipenv install
RUN apt-get update && apt-get install -y ffmpeg
ADD . /var/www/server