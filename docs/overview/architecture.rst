.. _architecture:

============
Architecture
============

This project is built as an extension of Apache `Superset <https://superset
.incubator.apache.org/>`__, which in turn is built on top of Flask
`AppBuilder <http://flask-appbuilder.readthedocs.io/en/latest/index.html>`__.

This document sumarizes the architecture from the point of view of
the application without any information about the deployment details. For the
project to work properly, however, it is important that it is deployed
correctly. To do this consistently, we provide a way to handle the
infrastructure via Docker. You can read more about it in the
:ref:`infrastructure <infrastructure>` document.

Dependencies
============

The project's dependencies are managed with `Pipenv <https://docs.pipenv.org/>`_.

Most dependencies are meant to be installed in the docker image and are not
necessary in the host machine. The only exception is `Fabric <https://pypi
.org/project/Fabric3/>`_ which you may need if you want to use the provided
shortcut commands.

Versioning and pinning
----------------------

The provided ``Pipfile`` doesn't contain pinned versions. The versions are
pinned in the ``Pipfile.lock`` file. Modifying the later may affect the way
the application behaves and/or require data migrations so you need to be
extra careful and test the application when changing it.

Keeping the ``Pipfile`` without pinned bersions allows us to update the
versions of all dependencies by just running::

    $ pipenv lock

This is particularly useful if you want to include upstream changes made to
superset.

Overrides
=========

To override superset, we are serving it with uWSGI via the configuration
files ``wsgi.py`` and ``uwsgi.ini``. The first one handles the configuration of
the app itself, and the second one the configuration of the uWSGI server.

We have built the machinery necessary to override or extend the following
pieces of superset:

 * Static files
 * Templates
 * CLI
 * Views

Static files
------------

Static file overrides are handled by serving static files from uWSGI if found
in the ``static/`` directory. Any request for static files will try to find
the files in that directory before the default files provided by superset.

Templates
---------

The templates are overridden in a similar manner but configured in ``wsgi.py``.

The template path from the project is injected into the Flask configuration for
jinja so that the application will attempt to find any templates in
``templates/`` before searching in the superset-provided template paths.

The specific setting modified here is ``app.jinja_loader.searchpath``

Views
-----

We have added two views. They can be found under ``chpro/views/``.

The first one, `LoadSQL`, allows users with an `Administrator` role to run
arbitrary SQL files on the database.

The second one, `EditorUserView`, allows users with an `Editor` role to
create, edit and delete `Viewers`.


Jinja Extensions
~~~~~~~~~~~~~~~~

At the moment, the only jinja extension provided is a context processor to
check the chpro-specific permissions (located at
``chpro/jinja_extensions/permissions.py``), and


CLI
---

To provide custom commands, we created a new `chpro` command configured in
``chpro/cli.py``. The command is defined by the executable
located at ``chpro/bin/chpro``. To define your own commands, see
:ref:writing_commands`

Loading extensions
==================

Some of the extensions configured in the ``wsgi.py`` file need to be "loaded",
meaning that they have a ``load()`` command that needs to be called for them to
take effect. That command is configured in the ``__init__.py`` of the
pertinent module. For example: ``chpro/views/__init__.py`` and
``chpro/jinja_extensions/__init__.py``.

Future extensions
=================

In general, extending the application is a matter of modifying the
configuration provided by the superset `app` or the `appbuilder`. To do that,
you need to::

    # Import the app and the appbuilder:
    from superset import app, appbuilder

    # And make modifications.

    # For example:

    # Add a path to the jinja loader
    app.jinja_loader.searchpath.insert(0, 'my/custom/template/path/')

    # Register a custom view
    from views.custom import MyCustomView
    appbuilder.add_view(MyCustomView, _('Custom View'))

    # Or register a CLI command:
    from flask_script import Command
    class MyCommand(Command):
        def run(self):
            print('This is a command')

    manager = Manager(app)
    manager.add_command('my_command', MyCommand)

