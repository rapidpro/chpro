from fabric.api import *

env.roledefs = {
    'local': ['localhost'],
    'staging': ['chpro@46.101.31.170'],
}

if not len(env.roles):
    env.roles = ['local']


def get_db_container():
    if 'local' in env.roles:
        return 'chpro-db'
    else:
        return run('docker ps -f name=production_db.1 -q')

def get_app_container():
    if 'local' in env.roles:
        return 'chpro_chpro_run_3'
    else:
        return run('docker ps -f name=production_chpro.1 -q')

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
    with settings(output_prefix=False):
        run("docker exec -it {container} bash -c '{command}'".format(
            command=command,
            container=get_app_container()
        ))
    print('--------\n\n')
