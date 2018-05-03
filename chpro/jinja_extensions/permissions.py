from flask import g
from superset import app

@app.context_processor
def chpro_roles():
    roles = [i.name for i in g.user.roles]
    return dict(user=g.user,
                is_admin='Chpro Admin' in roles,
                is_editor='Chpro editor' in roles,
                is_viewer='Chpro viewer' in roles)

