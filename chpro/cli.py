from flask_script import Manager
from superset import app, utils

config = app.config
celery_app = utils.get_celery_app(config)


from flask_script import Command

class Hello(Command):
    """prints hello world"""

    def run(self):
        print("hello world")

manager = Manager(app)
manager.add_command('hello', Hello())

