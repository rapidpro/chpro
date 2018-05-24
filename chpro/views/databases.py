import os

import sqlalchemy

from flask import Blueprint

from flask import flash, abort, g
from flask_appbuilder import SimpleFormView
from flask_babel import lazy_gettext as _
from six import text_type
from superset import app, appbuilder, utils
from werkzeug.utils import secure_filename, redirect

from chpro.forms.databases import LoadSQLForm
from superset_config import SQLALCHEMY_DATABASE_URI

config = app.config


# simple_page = Blueprint('simple_page', __name__, template_folder='templates')
#
#
# @simple_page.route('/', defaults={'page': 'index'})
# @simple_page.route('/<page>')
# def show(page):
#     return "Ok"
#
#
# app.register_blueprint(simple_page)


class LoadSQL(SimpleFormView):
    form = LoadSQLForm
    form_title = _('Database creation')
    add_columns = ['database', 'schema', 'table_name']

    def form_get(self, form):
        # Explicitly checking "Admin" permissions
        if 'Admin' not in [i.name for i in g.user.roles]:
            abort(401)

    def form_post(self, form):
        # Explicitly checking "Admin" permissions
        if 'Admin' not in [i.name for i in g.user.roles]:
            abort(401)

        # Note: This is intrinsically insecure.
        # Anyone with access to this view can execute custom commands on the DB.

        sql_file = form.sql_file.data
        form.sql_file.data.filename = secure_filename(form.sql_file.data.filename)
        sql_filename = form.sql_file.data.filename
        try:
            engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
            conn = engine.raw_connection()
            with conn.cursor() as cursor:
                cursor.execute(f"create database {form.db_name.data}")
                cursor.execute(f"use {form.db_name.data}")
                contents = sql_file.stream.read()
                commands = contents.decode().split(';\n')
                for command in commands:
                    if command.rstrip() != '':
                        cursor.execute(command)
            conn.commit()
            conn.close()
        except Exception as e:
            message = text_type(e)
            flash(
                message,
                'danger')
            return redirect('/loadsql/form')

        # Go back to welcome page / splash screen
        message = _(f'SQL file "{sql_filename}" uploaded database "{form.db_name.data}"')
        flash(message, 'info')
        return redirect('/tablemodelview/list/')


appbuilder.add_view(LoadSQL, 'LoadSQL',
                    category='Sources',
                    icon='fa-upload',)
