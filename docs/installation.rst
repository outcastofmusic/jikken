============
Installation
============

TODO: Install with pip
^^^^^^^^^^^^^^^^^^^^^^
Create PIP Install once v0.1 is feature complete


Install from Source
^^^^^^^^^^^^^^^^^^^

Jikken  can be installed from source. This installation is compatible with Linux/Mac OS X and Python 3.{4,5,6}. In order to use
mondoDB or elasticsearch a mongodb or es database need to be setup and running.

* git clone the library::

   git clone https://github.com/outcastofmusic/jikken.git

* run the setup install::

   python3 setup.py install


Database Configuration
^^^^^^^^^^^^^^^^^^^^^^

Jikken uses a configuration  file named `` config ``  with the database information it will use. It will look for it in
the experiment scripts directory in teh file ``$SCRIPT_DIR/.jikken/config ``. If it can't find a project specific config it will look
for a global one inside the  users HOME dir in the file `` ~/.jikken/config ``. If That doesn't exist either it will create it with default values using tinydb as the database.

The ``config`` file should look like this::

    [db]
    path = ~/.jikken/jikken_db/
    type = tiny
    name = jikken

Where:
- path is the path to the database (or a valid *uri* in the case of mongodb or es.
- type is the type of the database (valid options are: ``tiny``, ``mongo``, ``es``.
- name is the name of the database to use. Default is ``jikken``.

An example of a config file using mongo would be::

    [db]
    path = mongodb://localhost:27017
    type = mongo
    name = jikken

