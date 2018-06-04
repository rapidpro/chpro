.. _importing_rapidpro_data:

=======================
Importing RapidPro data
=======================

Overview
========

RapidPro data can be imported into the system via two commands that allow the
fetching of data from the RapidPro API.

For this to work, you need to have provided a valid `RAPIDPRO_KEY` in
the :ref:`secrets <required_secrets>`_ when setting up the server.

Running the commands
====================

The commands need to be run inside a running app container. This can be done
via directly using bash inside the container::

    chpro import_rapidpro_run <flow_id>

from the host through docker::

    docker exec -it `docker ps -f name=production_chpro.1 -q` chpro import_rapidpro_run <flow_id>

Or via fabric::

    fab -H user@host apprun:'chpro import_rapidpro_run <flow_id>'

Scheduling
==========

For the data to be up to date, the commands need to be executed regularly.
This means you will need some form of scheduling: typically a cron job.

Commands
========

To import RapidPro runs you need to specify the `flow_id`::

    chpro import_rapidpro_run <flow_id>

Contacts can be imported without any extra parameters::

    chpro import_rapidpro_contacts

Arguments
---------

Both commands take two arguments:

    * ``--after`` (or ``-a``) to specify a start date
    * ``--before`` (or ``-b``) to specify an end date

During the first run, all data will be imported. Subsequent runs will only
import new data.

If you want to force the commands to import data older than the latest
imported item, you'll need to do so by specifying an `after` argument

Querying the data
=================

The data will be imported into the ``rapidpro_run`` and ``rapidpro_contacts``
tables. These tables can be queried as any other, with the caveat that some
of the columns will be of type JSON.

For the contacts, the json columns will be:

 * groups
 * urns
 * fields

For the runs, the json columns will be:

 * path
 * values

Working with JSON columns
-------------------------

When querying JSON columns you should follow `mysql json syntax`_, an example
of which is the following SQL::

    select `rapidpro_run`.`values`->"$.vaccine1.category" as vaccine, modified_on
    from `rapidpro_run`
    where `rapidpro_run`.`values`->"$.vaccine1.category" is not NULL;


.. important::
    Note that the the tables are escaped using the `backtick` (`````) syntax.
    This is necessary because of the way superset builds the query internally.

    Failing to quote the tables this way may result in badly formatted
    queries and not provide the correct results.



Demos
=====

Visualizing RapidPro Runs
-------------------------

.. raw:: html

   <video controls width="640" src="/docs/_static/videos/VisualizingRapidProRuns.mov"></video>

Visualizing RapidPro Contacts
-----------------------------

.. raw:: html

   <video controls width="640"
   src="/docs/_static/videos/VizualizingRapidProContacts.mov"></video>


.. _mysql json syntax: https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#operator_json-column-path
