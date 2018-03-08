# Initial notes

## Documentation

 * Consider two ways to set it up:
   - Automated, one script all defaults
   - Manual, running all commands manually

## ToDo:

 * Specify a port to run on during installation
 * Generate a secret key when generating passwords
 * Style customizations
 * Document a way to load a database
 * Move secrets to `./ops/secrets.sample` and require `cp -r` for
   development

# Installing and running with Docker Compose (Development)

## Prerequisites

 * Install docker and docker-compose (ubuntu instructions?)

## Secrets

The sample secrets need to be available under `./ops/secrets`.

You need to create these secrets, but a set of sample secrets is
provided so you can use them in development mode. To use this run:

`cp -R ./ops/secrets.sample ./ops/secrets`


## Running

`docker-compose -f ./ops/docker-compose.yml --project-directory . up`

## First run

The first time the application is run, we must initialize the db:

`docker exec -it chpro-app fabmanager create-admin --app superset`

`docker exec -it chpro-app superset db upgrade`

`docker exec -it chpro-app superset init`

## Loading a Database form a MySQL dump



# Installing and running with Docker Swarm locally (Production)

## Prerequisites

 * Install docker

## Build the app

`docker build -t chpro -f ops/containers/app/Dockerfile .`

## Initialize the swarm

`docker swarm init`

## Secrets

 * Use the `generate_secrets.sh` script to generate the secrets

## First time run

Need to add these things to a script:

``docker exec -it `docker ps -f name=production_chpro.1 -q` <command>``

# Loading a data into the DB

?? ToDo

# Notes regarding the reorganization

If I follow through with the reorganization, we'll need to run:

`docker-compose -f ./ops/docker-compose.yml --project-directory . up`

and

`docker stack deploy -c ops/production.yml production`
