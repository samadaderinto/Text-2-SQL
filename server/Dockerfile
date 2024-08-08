FROM python:3

WORKDIR /var/www/server
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pip3 install --upgrade pip3 install pipenv
ADD Pipfile /var/www/server
ADD Pipfile.lock /var/www/server
RUN python3 -m pipenv install
ADD . /var/www/server
RUN chmod +x run.sh
CMD ["./run.sh"]
