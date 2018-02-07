FROM python:3.6.4

RUN set -ex && apt-get -q update && apt-get install libsasl2-dev && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LANG C.UTF-8

# -- Install Pipenv:
RUN set -ex && pip install pip pipenv --upgrade

# -- Create the workdir:
RUN set -ex && mkdir /app
WORKDIR /app

# -- Install dependencies:
ADD ./Pipfile /app/Pipfile
ADD ./Pipfile.lock /app/Pipfile.lock
RUN set -ex && pipenv install --deploy --system

# -- Install Application into container:
ADD . /app

# -- Make sure the superset configuration will be discoverable
ENV PYTHONPATH $PYTHONPATH:/app

EXPOSE 9090

ENTRYPOINT ["uwsgi"]
CMD ["--ini", "/app/uwsgi.ini"]