# Local development

## Building manually (optional)

You should probably skip this step unless you have a reason to build
the application manually.

To build it, run:

`docker build -t chpro -f ops/containers/app/Dockerfile .`

This will build an image the same way as it's built for production.

### Building for development

If you want to build the image for development (and allow debugging
with ipdb), you can use:

`docker build -t chpro -f ops/containers/app/Dockerfile . --build-arg PIPENV_ARGS="--dev"`

## Running

The simplest way to run the application locally is using docker compose:

`docker-compose -f ./ops/docker-compose.yml --project-directory . up --build`

If you have built the application manually and wish to use that build
instead, you can skip the  `--build` flag and just run:

`docker-compose -f ./ops/docker-compose.yml --project-directory . up`

## Editing files

The application directory is mounted for local development. Editing the
files in your filesystem will be reflected in the running container.

## Restarting the server

However, for the changes to take effect in the running container, you
need to restart the server. To do that, you can:

`touch uwsgi.ini`

## Debugging with ipdb

To be able to debug with pdb/ipdb, you need to run the application manually:

`docker-compose -f ./ops/docker-compose.yml --project-directory . run --service-ports chpro`


