
def get_secret(secret_name):
    try:
        with open('/run/secrets/{0}'.format(secret_name), 'r') as secret_file:
            return secret_file.read().strip()
    except IOError:
        return None

MYSQL_PASSWORD = get_secret('MYSQL_PASSWORD')
MYSQL_ROOT_PASSWORD = get_secret('MYSQL_ROOT_PASSWORD')

SQLALCHEMY_DATABASE_URI = f'mysql://superset:{MYSQL_PASSWORD}@db/superset?charset=utf8'
SQLALCHEMY_ROOT_DATABASE_URI = f'mysql://root:{MYSQL_ROOT_PASSWORD}@db/?charset=utf8'

MAPBOX_API_KEY = 'pk.eyJ1Ijoibmljb2xhc2xhcmEiLCJhIjoiY2pkMXJ1Z2Y5MGNrazMzbG9kZWMyNXN2dSJ9.DRkSouvQhfYPbCWChW6Q-g'

RAPIDPRO_API_KEY = get_secret('RAPIDPRO_API_KEY')

APP_NAME = "RapidPro"
APP_THEME = "rph.css"

SECRET_KEY = get_secret('SECRET_KEY')

# Change this to setup a new logo
# APP_ICON = '/static/assets/images/superset-logo@2x.png'

# Registering blueprints here won't work because of import order
# Instead, we register them where we define them and make sure they are loaded
# at app initialization
BLUEPRINTS = []

LANGUAGES = {
    'en': {'flag': 'us', 'name': 'English'},
    'fr': {'flag': 'fr', 'name': 'French'},
}
