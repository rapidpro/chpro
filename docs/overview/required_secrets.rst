.. _required_secrets:

================
Required Secrets
================

The following secrets are required for the application to run:

 * DOCS_PASSWORD
 * DOCS_USER
 * MYSQL_PASSWORD
 * MYSQL_ROOT_PASSWORD
 * RAPIDPRO_API_KEY

To generate them automatically run::

    fab generate_secrets

.. note:: If you want to generate the secrets for a specific environment,
   check the documentation on using the fabric commands.

Manually working with secrets
-----------------------------

