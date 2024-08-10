FROM python:3.7.16
WORKDIR /var/www/pearmonie
RUN pip3 install pipenv
ADD Pipfile /var/www/pearmonie
ADD Pipfile.lock /var/www/pearmonie
RUN python3 -m pipenv install
ADD . /var/www/pearmonie