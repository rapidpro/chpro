.. _overview:

========
Overview
========

This project is built as an extension of Apache `Superset <https://superset
.incubator.apache.org/>`__. As a user of the dashboard, main features you may
be interested in are those of Superset itself. As such, before using the
dashboard you should familiarize yourself with the `usage documentation`_
provided by superset.

Permissions
===========

The permission system has been setup so that the following roles are available:

Administrator
-------------

This corresponds to the default Superset `administrator <https://superset.incubator.apache.org/security.html#admin>`__.

Editor
------

The editor is based Superset's `alpha <https://superset.incubator.apache
.org/security.html#alpha>`__ role but extended to be able to use the SQL lab
and `manage the users with a "viewer" role <managing_viewers>`__.

Viewer
------

The editor is based Superset's `gamma <https://superset.incubator.apache
.org/security.html#gamma>`__ role but limited so that users with this role
only have the ability to view the dashboards.

Extensions
==========

Beyond the standard feature set of superset. We provide the following
extensions:

 * :ref:`Importing a SQL file <importing_sql>`
 * :ref:`Managing Viewers <managing_viewers>`
 * :ref:`Importing RapidPro data <importing_rapidpro_data>`


.. _usage documentation: https://superset.incubator.apache.org/tutorial.html



