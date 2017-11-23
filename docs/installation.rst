============
Installation
============

TODO: Install with pip
^^^^^^^^^^^^^^^^^^^^^^
Create PIP Install once v0.1 is feature complete


Install from Source
^^^^^^^^^^^^^^^^^^^

Jikken  can be installed from source. This installation is compatible with Linux/Mac OS X and Python `3.{5,6}`. In order to use
mongoDB or elasticsearch a database need to be setup and running already.

* git clone the library

.. code-block:: bash

   git clone https://github.com/outcastofmusic/jikken.git

* run the setup install

.. code-block:: bash

   python3 setup.py install


Database Configuration
^^^^^^^^^^^^^^^^^^^^^^

Jikken uses a configuration  file named `config`  with the database information it will use. It will look for it in
the experiment scripts directory in teh file `$SCRIPT_DIR/.jikken/config`. If it can't find a project specific config it will look
for a global one inside the  users HOME dir in the file `~/.jikken/config`. If That doesn't exist either it will create it with default values using tinydb as the database.

The `config` file should look like this

.. code-block:: ini

    [db]
    path = ~/.jikken/jikken_db/
    type = tiny
    name = jikken

Where:
- path is the path to the database (or a valid *uri* in the case of mongodb or es.
- type is the type of the database (valid options are: `tiny`, `mongo`, `es` (ES not implemented yet).
- name is the name of the database to use. Default is `jikken`.

An example of a config file using *Mongo* would be

.. code-block:: ini

    [db]
    path = mongodb://localhost:27017
    type = mongo
    name = jikken

An example of a config file using *ElasticSearch* would be

.. code-block:: ini

    [db]
    path = http:://localhost:9200
    type = es
    name = jikken

Setup MongoDB using docker
^^^^^^^^^^^^^^^^^^^^^^^^^^

pull the mongodb image:

.. code-block:: bash

    docker pull mongo


then run the image. You can use the `-p` flag to map the port to a localport (that matches the one in the config file
and also mount a local folder where the db will be located

.. code-block:: bash

    docker run --name jikken-mongo -p $LOCALPORT:27017 -v $LOCALPATH:/data/db -d mongo

For more info see the official `docker mongo`_ information.


Setup ES using docker
^^^^^^^^^^^^^^^^^^^^^

pull the es image:

.. code-block:: bash

    docker pull docker.elastic.co/elasticsearch/elasticsearch-oss:6.0.0

then run the image. (this command is for development mode):


.. code-block:: bash

    docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch-oss:6.0.0


For more info see the official `docker es`_ guide.


.. _docker es: https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html
.. _docker mongo: https://hub.docker.com/_/mongo/