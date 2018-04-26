from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from flask_appbuilder.forms import DynamicForm
from flask_wtf.file import FileRequired, FileAllowed
from flask_babel import lazy_gettext as _

from superset import app, db
from superset.models import core as models
from wtforms import StringField, FileField
from wtforms.validators import DataRequired


class LoadSQLForm(DynamicForm):
    # pylint: disable=E0211
    def all_db_items():
        return db.session.query(models.Database)

    db_name = StringField(
        _('Database Name'),
        description=_('Name of the database to create based on the SQL file.'),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget())
    sql_file = FileField(
        _('SQL File'),
        description=_('Select a SQL file to be executed on a new database.'),
        validators=[
            FileRequired(), FileAllowed(['sql'], _('SQL Files Only!'))])
