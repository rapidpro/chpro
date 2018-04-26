import os

from superset import app
from chpro import views

config = app.config

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
app.jinja_loader.searchpath.insert(0, os.path.join(PROJECT_DIR, 'templates'))

views.load()
