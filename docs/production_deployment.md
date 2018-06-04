# Production deployment (Manual)

## Introduction

This is a guide for setting up the chpro dashboard on a ubuntu box.

## Set up a user (optional)

 `adduser chpro`

 `usermod -aG sudo chpro`

 You may also want your ssh public key to
 `/home/chpro/.ssh/authorized_keys`

## Clone the repository

 `git clone https://github.com/rapidpro/chpro.git`

## Install docker

 From your home directory, run:

 `chpro/ops/scripts/get-docker.sh`

 Then add your user to the docker group:

 `sudo usermod -aG docker chpro`

 You will need to ssh again to the server to use docker.

## Run the application

 The following commands will be run from the inside the checked out repo.

### Build the container

`docker build -t chpro -f ops/containers/app/Dockerfile .`

## Initialize the swarm

`docker swarm init`

If you have multiple ips you may need to run

`docker swarm init --advertise-addr <ip>`

If you don't know your external ip, you can get it via
`curl ipinfo.io/ip`

## Secrets

The following secrets need to be available as files with the same name as the
secret in ``/run/secrets/`` in the app container for the project to work

 * SECRET_KEY
 * MYSQL_PASSWORD
 * MYSQL_ROOT_PASSWORD
 * RAPIDPRO_API_KEY
 * DOCS_PASSWORD
 * DOCS_USER

The easiest way to generate the secrets is using the 
[fabric command](guides/using_the_fabric_shortcuts.html)

### SECRET_KEY

To generate a secert key, you can run:

```
python -c 'import random; print("".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]))'
``` 

## First run

Run the following commands:

``docker exec -it `docker ps -f name=production_chpro.1 -q` fabmanager create-admin --app superset``

``docker exec -it `docker ps -f name=production_chpro.1 -q` superset db upgrade``

``docker exec -it `docker ps -f name=production_chpro.1 -q` superset init``

``docker exec -it {} chpro setup_permissions``

``docker exec -it {} chpro custom_post_install_fixes``

## Loading the DBs

To load the data in the for the application you can create a database and 
then run:

``docker exec `docker ps -f name=production_db.1 -q` bash -c 'mysql --user=superset --password="$(cat /run/secrets/MYSQL_PASSWORD)" -D zambia_immun' < ~/zambia_immun.sql``
