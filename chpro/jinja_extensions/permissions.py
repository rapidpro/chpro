from flask import g
from superset import app


@app.context_processor
def chpro_roles():
    try:
        roles = [i.name for i in g.user.roles]
    except AttributeError:
        return {}
    return dict(user=g.user,
                is_admin='Admin' in roles,
                is_editor='Editor' in roles,
                is_viewer='Viewer' in roles)

