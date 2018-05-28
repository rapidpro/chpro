from flask_script import Manager

from superset import app

from chpro.commands.rapidpro_import import ImportRapidProRun
from chpro.commands.initial_setup import SetupPermissions, \
    CustomPostInstallFixes


manager = Manager(app)
manager.add_command('import_rapidpro_run', ImportRapidProRun())
manager.add_command('custom_post_install_fixes', CustomPostInstallFixes())
manager.add_command('setup_permissions', SetupPermissions())
