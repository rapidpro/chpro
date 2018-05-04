FROM python:3.6.4

ARG PIPENV_ARGS

RUN set -ex && apt-get -q update && apt-get install -y \
    libsasl2-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LANG C.UTF-8

# -- Install Pipenv:
RUN set -ex && pip install pip pipenv --upgrade

# -- Create the workdir:
RUN set -ex && mkdir /app
WORKDIR /app

ADD ./Pipfile /app/
ADD ./Pipfile.lock /app/

# -- Install dependencies:
RUN set -ex && pipenv install --deploy --system --ignore-pipfile $PIPENV_ARGS

# -- Install Application into container:
ADD . /app

# -- Install the application itself:
RUN set -ex && pip install -e .

# -- Make sure the superset configuration will be discoverable
ENV PYTHONPATH $PYTHONPATH:/app

EXPOSE 9090

ENTRYPOINT ["uwsgi"]
CMD ["--ini", "/app/uwsgi.ini"]
