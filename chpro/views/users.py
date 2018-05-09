from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.sqla.models import User
from flask_appbuilder.security.views import UserModelView

from superset import app, appbuilder
from werkzeug.exceptions import abort


class FilteredSQLAInterface(SQLAInterface):
    def _get_base_query(self, query=None, filters=None, order_column='', order_direction=''):
        base = super()._get_base_query(query=query, filters=filters,
                                       order_column=order_column, order_direction=order_direction)
        return base.filter(User.roles.any(name='Viewer'))


class EditorUserView(UserModelView):
    datamodel = FilteredSQLAInterface(User)
    route_base = '/eusers'

    def _add(self):
        # We're limiting the restriction to the UI to avoid editors from assigning bad permissions.
        # Editors should be trusted not to maliciously send bad arguments for roles.
        widget = super()._add()
        if widget and widget.get('add', {}) and widget['add'].template_args:
            form = widget['add'].template_args['form']
            form.roles._get_object_list()
            form.roles._object_list = [i for i in form.roles._object_list if i[1].name == 'Viewer']
        return widget

    def _edit(self, pk):
        item = self.datamodel.get(pk, self._base_filters)
        if not item:
            abort(404)

        if 'Viewer' not in [i.name for i in item.roles]:
            abort(404)

        # We're limiting the restriction to the UI to avoid editors from assigning bad permissions.
        # Editors should be trusted not to maliciously send bad arguments for roles.
        widget = super()._edit(pk)
        if widget and widget.get('edit', {}) and widget['edit'].template_args:
            form = widget['edit'].template_args['form']
            form.roles._get_object_list()
            form.roles._object_list = [i for i in form.roles._object_list if i[1].name == 'Viewer']
        return widget


appbuilder.add_view(EditorUserView, 'Manage Viewers',
                    icon='fa-user')
