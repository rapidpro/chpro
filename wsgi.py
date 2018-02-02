import os
from superset import app, db, dict_import_export_util, security, utils

config = app.config

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
app.jinja_loader.searchpath.insert(0, os.path.join(PROJECT_DIR, 'templates'))
