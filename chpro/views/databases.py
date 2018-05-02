import os

import sqlalchemy

from flask import Blueprint

from flask import flash
from flask_appbuilder import SimpleFormView
from flask_babel import lazy_gettext as _
from six import text_type
from superset import app, appbuilder, utils
from werkzeug.utils import secure_filename, redirect
from sqlalchemy.sql import text

from chpro.forms.databases import LoadSQLForm
from superset_config import SQLALCHEMY_DATABASE_URI

config = app.config


simple_page = Blueprint('simple_page', __name__, template_folder='templates')


@simple_page.route('/', defaults={'page': 'index'})
@simple_page.route('/<page>')
def show(page):
    return "Ok"


app.register_blueprint(simple_page)


class LoadSQL(SimpleFormView):
    form = LoadSQLForm
    form_title = _('Database creation')
    add_columns = ['database', 'schema', 'table_name']

    def form_get(self, form):
        pass

    def form_post(self, form):
        # ToDo: Do we really want to do this? This would inherently be insecure.
        # ToDo: Check permissions
        sql_file = form.sql_file.data
        form.sql_file.data.filename = secure_filename(form.sql_file.data.filename)
        sql_filename = form.sql_file.data.filename
        path = os.path.join(config['UPLOAD_FOLDER'], sql_filename)
        try:
            #utils.ensure_path_exists(config['UPLOAD_FOLDER'])
            sql_file.save(path)
            engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
            conn = engine.connect()
            conn.execute("commit")
            conn.execute(text("create database :db_name"), db_name=form.db_name.data)
            # ToDo: Start a subprocess here to load the DB.
            conn.close()
            # ToDo: Consider doing this in the backgrpound.
        except Exception as e:
            try:
                os.remove(path)
            except OSError:
                pass
            message = text_type(e)

            flash(
                message,
                'danger')
            return redirect('/loadsql/form')

        os.remove(path)
        # Go back to welcome page / splash screen
        db_name = 'DB NAme'
        message = _('SQL file "{0}" uploaded to table "{1}" in '
                    'database "{2}"'.format(sql_filename,
                                            form.name.data,
                                            db_name))
        flash(message, 'info')
        return redirect('/tablemodelview/list/')


appbuilder.add_view(LoadSQL, 'LoadSQL')
appbuilder.add_link(
    'Load SQL',
    label=_('Load SQL'),
    href='/loadsql/form',
    icon='fa-upload',
    category='Sources',
    category_label=_('Sources'),
    category_icon='fa-wrench')
