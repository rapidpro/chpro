# Production deployment

## Introduction

This is a guide for setting up the chpro dashboard on a ubuntu box.

ToDo: This should be automated with fabric.

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

Use the `generate_secrets.sh` script to generate the secrets:

`ops/scripts/generate_secrets.sh`

## First run

Run the following commands:

``docker exec -it `docker ps -f name=production_chpro.1 -q` fabmanager create-admin --app superset``

``docker exec -it `docker ps -f name=production_chpro.1 -q` superset db upgrade``

``docker exec -it `docker ps -f name=production_chpro.1 -q` superset init``

## Loading the DBs

ToDo: Create a script for loading DBs

Create a new db.

Load the data:

``docker exec `docker ps -f name=production_db.1 -q` bash -c 'mysql --user=superset --password="$(cat /run/secrets/MYSQL_PASSWORD)" -D zambia_immun' < ~/zambia_immun.sql``