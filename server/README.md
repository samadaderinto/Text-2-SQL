# Pearmonie Backend

This is the system that powers the entire PearMonie infrastructure. The PearMonie backend is a dockerized  Django and Django rest framework application. The bucket application runs in two modes;  the production mode "prod"  and the development mode "dev". 


## Installation

Required initial dependencies for this project are as follows;

a) python3

b) pipenv

c) docker


Required files for installation are as follows;

a) .env file (this is scaffolded for you in .env.example. ask the devs to provide the required values for your local computer)

b) pm.json (this prrovides Google Firebase credentials)


with these files in the root  directory,  from the following commands to install all necessary dependencies and start the backend container


```bash
$ docker-compose build
$ docker-compose up
```


Development environments and development dependencies

a) docker-compose

Docker-compose  is used to rapidly build and deploy the PearMonie backend image.  It is installable through pip3 and requires that docker is installed.


pip3 install docker-compose


b) invoke

invoke he's a task executor that is used to simplify the commands used to interact with the docker container from the host system.

example:


`$ python3 -m invoke manage makemigrations`


please note that invoke has to be installed in the host system and not in the docker image. It is not compulsory for the programmer to use invoke for all necessary commands this is just a simplified method of executing commands in the docker container.


## Initial database migration

when setting up the project for the first time the programmer has to first of all create a database on his or her local system or wherever the database may be and seed it  with the database structure of the previous implementation of this project (ask the development team for the MySQL dump for this)



```sql
mysql# create database pearmonie;

mysql# grant all privileges on pearmonie.* to '<username>'@'localhost' identified by '<password>';

mysql# exit;
```

import the dump as follows

```bash 
$ mysql -u <username> pearmonie < path/to/mysqldump.sql> -p
```



after setting up the dump  proceed to run the database migration as follows


```bash
# using invoke
$ python3 -m invoke manage migrate

# using docker-compose
$ docker-compose run pearmonie pipenv run python3 manage.py migrate
```


## Deployment

the guitar depository maintains two main branches, main and dev.  Attached to this branches specific workflows that handle deployment  to the various deployment servers. The main branch  is connected to a workflow that specifically deploys the application to the production server. This means that any comment that is pushed to the origin will automatically be acted upon and deployed to the production server. The same goes for the development server which uses the dev branch.


```
main -> production server

dev -> development server
```


these workflows can be found in /.github/workflows/  directory.



## Linting and formatting

the project uses a precommit hook that can be set on the local system. the preferred linter is called Black.

