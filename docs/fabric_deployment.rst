=====================
Deploying with Fabric
=====================

Fabric shortcuts are provided to simplify working with the application
in production (or a production-like local setup)

Requirements
============

Fabric needs to be installed to be able to use the commands.

You can manually install it running ``pip install fabric3``, but the
easiest way to get it setup is to install all the project's dependencies with
the pinned versions by running::

    pipenv install

And then to activate the environment::

    pipenv shell


Using Fabric
============

If you're unfamiliar with fabric, you may want to take a look at the
documentation at http://docs.fabfile.org/en/2.1/.

For this project, the main arguments you will be interested in are::

    fab -H user@host <command>  # Specifying a host manually
    fab -R <role> <command>  # Specifying a role manually

The provided roles are ``localhost`` and ``swarm_managers``.

If you don't provide a host or a role, `localhost` will be used as a default

Bootstrapping a new server
==========================

Bootstrapping a new server has been tested with Ubuntu 16.04 instances in
Digial Ocean. You need to be able to access the server as root.

To bootstrap a new server, run::

    fab -H user@host bootstrap

and follow the instructions.

You will be prompted to provide:

 * Authorization information for the chpro user (a ssh key or password)
 * The secrets to be used by the service
 * If you choose to deploy the application directly, information about the
   admin user to be used

.. note::
    You can generate a SECRET_KEY locally by running ``python -c 'import random; print("".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]))'``

Please make sure to remove root access after the server has been bootstrapped.

Deploying
=========

To deploy the application to all swarm managers run::

    fab -R swarm_managers deploy

This will build the container and deploy it to the configured swarm managers.

If you wish to deploy to a specific server, you can run::

    fab -H user@host deploy

.. warning::
    It is important to note that the image will be built based on the code
    you have available locally, so make sure you are in the correct branch
    and there aren't any unwanted code changes before running this command.

Accessing the DB
================

A shortcut is provided to access the DB shell. To use it, run::

    fab -H user@host mysql

Accessing the app
=================

A shortcut is provided to access the application container. To use it, run::

    fab -H user@host bash

