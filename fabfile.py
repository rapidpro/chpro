import itertools

from fabric.api import *

env.roledefs = {
    'local': ['localhost'],
    'staging': ['chpro@46.101.31.170'],
}

if not len(env.roles):
    env.roles = ['local']


env.colorize_errors = True


def get_db_container():
    if 'local' in env.roles:
        return 'chpro-db'
    else:
        return run('docker ps -f name=production_db.1 -q')


def get_app_container():
    if 'local' in env.roles:
        return 'chpro-app'
    else:
        return run('docker ps -f name=production_chpro.1 -q')


@task
def generate_secrets():
    return


@task
@runs_once
def bootstrap():
    if env.host in itertools.chain.from_iterable(env.roledefs.values()):
        raise Exception('Host is already defined in a role. Bootstrap should '
                        'only be used on new hosts.')
    # Create the chpro user
    sudo('id -u chpro &>/dev/null || adduser --disabled-password --gecos "" --quiet chpro')
    sudo('usermod -aG sudo chpro')
    # ToDo: Add a ssh key or pw
    sudo('sudo -u chpro git clone https://github.com/rapidpro/chpro.git /home/chpro/chpro')
    sudo('/home/chpro/chpro/ops/scripts/get-docker.sh')
    sudo('rm -Rf /home/chpro/chpro')
    sudo('sudo usermod -aG docker chpro')
    sudo('docker swarm init')
    generate_secrets()
    # ToDo: Initialize the application

@task
def mysql():
    with settings(output_prefix=False):
        run("docker exec -it {container} bash -c 'mysql --user={user} --password=\"$(cat /run/secrets/{secret})\"'".format(
            user='superset',
            secret='MYSQL_PASSWORD',
            container=get_db_container()
        ))


@task
def apprun(command):
    print('\n\n--------')
    with settings(output_prefix=False, remote_interrupt=True):
        run("docker exec -it {container} bash -c '{command}'".format(
            command=command,
            container=get_app_container()
        ))
    print('--------\n\n')


@task
def build_image():
    local('docker build -t chpro:production -f ops/containers/app/Dockerfile .')


@task
def export_image():
    local('docker save chpro:production | gzip > chpro.tar.gz')


@task
@roles('staging')
def deploy():
    build_image()
    export_image()

    # Upload the latest image
    put('chpro.tar.gz', '')
    run('gunzip -c chpro.tar.gz | docker load ')

    # Update the config if necessary
    with cd('chpro'):
        run('git pull')
        run('docker stack deploy -c ops/production.yml production')

    # Update the app
    run('docker service update production_chpro --force')

    # Cleanup
    run('rm chpro.tar.gz')
    local('rm chpro.tar.gz')
