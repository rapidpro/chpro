import itertools

from fabric.api import *
from fabric.contrib import files, console

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
    #import ipdb; ipdb.set_trace()
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

    can_login = False
    if console.confirm('Do you wish to add an authorized ssh key for the '
                       'chpro user?', default=False):
        sudo('sudo -u chpro -- mkdir -p /home/chpro/.ssh')
        files.append(
            '/home/chpro/.ssh/authorized_keys',
            prompt('Please paste the desired ssh public key (i.e. ~/.ssh/id_rsa.pub):'),
            use_sudo=True
        )
        can_login = True
    if not can_login:
        if console.confirm('Do you wish to add password for the '
                           'chpro user?', default=False):
            sudo('passwd chpro')
            can_login = True
    if not can_login:
        raise Exception('You will not be able to login as the chpro user. '
                        'Make sure to provide a password or a ssh key')

    sudo('sudo -u chpro git clone https://github.com/rapidpro/chpro.git /home/chpro/chpro')
    sudo('/home/chpro/chpro/ops/scripts/get-docker.sh')
    sudo('sudo usermod -aG docker chpro')
    # ToDo: Add option to bootstrap a server that will join an existing swarm
    sudo('docker swarm init')
    if console.confirm('You will need secrets for the application to run. '
                       'Do you wish to generate them?'):
        generate_secrets()


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
def deploy(first_time=False):
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

    if first_time:
        if console.confirm('Do you wish to initialize the database? If you '
                           'choose not to do this, the application will not '
                           'run and you will need to initialize the DB '
                           'manually', default=True):
            pass
