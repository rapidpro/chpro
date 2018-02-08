print('loading custom config')


def get_secret(secret_name):
    try:
        with open('/run/secrets/{0}'.format(secret_name), 'r') as secret_file:
            return secret_file.read().strip()
    except IOError:
        return None


CHPRO_MYSQL_PASSWORD = get_secret('CHPRO_MYSQL_PASSWORD')

SQLALCHEMY_DATABASE_URI = f'mysql://superset:{CHPRO_MYSQL_PASSWORD}@db/superset'

MAPBOX_API_KEY = 'pk.eyJ1Ijoibmljb2xhc2xhcmEiLCJhIjoiY2pkMXJ1Z2Y5MGNrazMzbG9kZWMyNXN2dSJ9.DRkSouvQhfYPbCWChW6Q-g'

# Change this to setup a new logo
# APP_ICON = '/static/assets/images/superset-logo@2x.png'

print(SQLALCHEMY_DATABASE_URI)
