import itertools
import time

from fabric.api import *
from fabric.contrib import files, console

# ToDo: Define hosts externally
env.roledefs = {
    'local': ['localhost'],
    'swarm_managers': ['chpro@46.101.31.170', 'chpro@178.62.122.53'],
}

role_map = {}
for role in env.roledefs:
    for host in env.roledefs[role]:
        role_map[host] = role

if not len(env.roles) and not len(env.hosts):
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
        return run("docker ps -f name=production_chpro.1 --format '{{.CreatedAt}} *{{.ID}}' -q | sort -r | cut -d '*' -f 2").split()[0]


@task
def generate_secret(key=None, value=None):
    if not key or not value:
        raise Exception('Please provide a key and a value for the secret')

    if 'local' in env.roles:
        local('mkdir -p ops/secrets')
        local('echo "{}" > ops/secrets/{}'.format(value, key))
        return

    with settings(user='chpro'):
        run('echo {} | docker secret create {} -'.format(value, key))



SECRET_LIST = [
    'SECRET_KEY',
    'MYSQL_PASSWORD',
    'MYSQL_ROOT_PASSWORD',
    'RAPIDPRO_API_KEY',
    'DOCS_PASSWORD',
    'DOCS_USER',
]

@task
def prompt_for_secrets():
    print('Generating all secrets required for the application to run...')
    for key in SECRET_LIST:
        value = prompt('Please provide a value for secret "{}" '
                       '(Leave empty to ignore): '.format(key))
        if value:
            generate_secret(key, value)
    return


@task
def bootstrap():
    if env.host in [i.strip('chpro@') for i in itertools.chain.from_iterable(env.roledefs.values())]:
        raise Exception('Host is already defined in a role. Bootstrap should '
                        'only be used on new hosts.')

    # Create the chpro user
    sudo('id -u chpro &>/dev/null || adduser --disabled-password --gecos "" --quiet chpro')
    sudo('usermod -aG sudo chpro')

    can_login = False
    if console.confirm('Do you wish to add an authorized ssh key for the '
                       'chpro user?', default=False):
        run('sudo -u chpro -i mkdir -p /home/chpro/.ssh')
        with settings(sudo_prefix="sudo -u chpro -i -p '%(sudo_prompt)s' " % env):
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

    # ToDo: should we use put() instead of git? We need the network anyway to get docker
    run('sudo -u chpro -i git clone https://github.com/rapidpro/chpro.git /home/chpro/chpro')
    sudo('/home/chpro/chpro/ops/scripts/get-docker.sh')
    sudo('usermod -aG docker chpro')

    # ToDo: Add option to bootstrap a server that will join an existing swarm
    sudo('docker swarm init --advertise-addr {}'.format(env.host))
    if console.confirm('You will need secrets for the application to run. '
                       'Do you wish to generate them?'):
        prompt_for_secrets()

    if console.confirm('Do you wish to deploy the application on the server right now?'):
        deploy(first_time=True)
        print('''
        The server has been successfully bootstrapped and deployed.
        
        To continue managing the server via fabric, make sure to add a role definition for it, i.e.:

        env.roledefs = {{
        'local': ['localhost'],
        'some_environment': ['chpro@{}']  # <-- Like this
        'staging': ['chpro@46.101.31.170'],
        }}        
        '''.format(env.host))
    else:
        print('''
        The server has been successfully bootstrapped and it's ready for a deployment.
        
        To do this, please add a role for the server i.e.:
        
        env.roledefs = {{
        'local': ['localhost'],
        'swarm_managers': ['chpro@{}']  # <-- Like this
        'staging': ['chpro@46.101.31.170'],
        }}
    
        and then run a deploy for that environment:
        
        $ fab -R swarm_managers deploy     
        '''.format(env.host))


@task
def apprun(command):
    print('\n\n--------')
    with settings(output_prefix=False, remote_interrupt=True):
        open_shell("docker exec -it {container} bash -c '{command}'".format(
            command=command,
            container=get_app_container()
        ))
    print('--------\n\n')


@task
def mysql():
    with settings(output_prefix=False, remote_interrupt=True):
        open_shell("docker exec -it {container} bash -c 'mysql --user={user} --password=\"$(cat /run/secrets/{secret})\"'; exit".format(
            user='superset',
            secret='MYSQL_PASSWORD',
            container=get_db_container()
        ))


@task
def bash():
    with settings(output_prefix=False, remote_interrupt=True):
        open_shell("docker exec -it {container} bash; exit".format(
            container=get_app_container()
        ))


@task
@runs_once
def build_image():
    local('docker build -t chpro:production -f ops/containers/app/Dockerfile .')


@task
@runs_once
def export_image():
    local('docker save chpro:production | gzip > chpro.tar.gz')


@task
def initialize(create_admin=False):
    """Initializes the database if running for the first time"""
    container = get_app_container()
    if create_admin:
        run('docker exec -it {} fabmanager create-admin --app superset'.format(container))
    run('docker exec -it {} superset db upgrade'.format(container))
    run('docker exec -it {} superset init'.format(container))
    run('docker exec -it {} chpro setup_permissions'.format(container))
    run('docker exec -it {} chpro custom_post_install_fixes'.format(container))


@task
@with_settings(user='chpro')
def deploy(first_time=False):
    build_image()
    export_image()

    # Upload the latest image
    put('chpro.tar.gz', '')
    run('gunzip -c chpro.tar.gz | docker load ')

    # Update the config if necessary
    with cd('/home/chpro/chpro'):
        run('git pull')  # ToDo: Should we consider a missing outside network here?
        run('docker stack deploy -c ops/production.yml production')

    if first_time:
        if console.confirm('Do you wish to initialize the database? If you '
                           'choose not to do this, the application will not '
                           'run and you will need to initialize the DB '
                           'manually', default=True):
            initialize(create_admin=True)
    else:
        # Update the app
        run('docker service update production_chpro --force -q')
        # Newer versions of superset may require a db upgrade
        run('docker exec -it {} superset db upgrade'.format(get_app_container()))

    # Cleanup
    run('rm chpro.tar.gz')
