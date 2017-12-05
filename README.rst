***********
Jikken 実験
***********

.. image:: https://travis-ci.org/outcastofmusic/jikken.svg?branch=master
    :alt: CLI Status
.. image:: https://readthedocs.org/projects/jikken/badge/?version=latest
    :alt: Documentation Status


**Jikken**  is a lightweight cli experiment manager for scientific experiments written in python.

It makes very few assumptions on the experiment and requires almost zero code changes
to the scripts. In fact the only assumption is that the main function of the script to be run
accepts a positional argument with either a directory with json/yaml config files
or a path to single json/yaml file. That's it. Optionally if the code of the
experiment is in a git repo, the git info will be added as well.


Features
########

- Python 3.{5,6} code
- Support for TinyDB, MongoDB, and ES
- tagging of experiments
- CLI to access experiment data
- only requires the script to load the variables from a file or folder
- support for json/yaml configs
- understands git directories

Installation
###############

Jikken can be installed from pip. This installation is compatible with Linux/Mac OSX and Python 3.5 or greater is required. To install the package use:


.. code-block::bash

    pip install jikken


or if the default python on your system is 2.7 use instead

.. code-block:: bash

    pip3 install jikken


Usage Example
#############

The main goal of *Jikken* is to require as little changes to your experiment code as possible. It's main assumption is that you have a script that runs an experiment and that
the scripts accepts at least a positional argument with the location of the experiment's config.
e.g. Let's assume you have an experiment runs by running my_experiment.py and it reads its configuration from a yaml file myconfig.yaml you would run it with:

.. code-block:: bash

    python my_experiment.py myconfig.yaml

Then in order to let jikken record the experiment you would run instead:

.. code-block:: bash

    jikken run my_experiment.py -c myconfig.yaml -n "my first experiment"

Jikken will then capture the config, Start the experiment, capture stdout and stderr, and save the information in the database as set in the config file.


Documentation
#############

The full documentation of jikken can be found  `here <http://jikken.readthedocs.io/en/latest/>`_

Contributing
------------

1. Fork it `here <https://github.com/outcastofmusic/jikken/fork>`_
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request


Release History
----------------

* 0.2.1
    * Fixed bug with updated monitored  (and added test)
    * Added cli delete command for both experiments and multistage experiments
    * refactored documentation a bit

* 0.2.0
    * Added mongodb and ES support
    * Added support for multistage experiments
    * started writing documentation on read the docs

* 0.1.0
    * Work in progress

Versioning
----------

We use `SemVer <http://semver.org/>`_ for versioning. For the versions available, see the `tags on this repository`_

Authors
-------

* **Agis Oikonomou** - *Initial work*

License
-------

This project is licensed under the MIT License - see the `LICENSE`_ file for details

Acknowledgments
---------------

* Brian Okken and his great book on python testing and a great influence on the structure of the code: `Python Testing with Pytest`_.
* Francois Chollet and his book `Deep Learning with Python`_. The examples of jikken are all based on the ones from the book.


.. _CLI Status: https://travis-ci.org/outcastofmusic/jikken.svg?branch=master
.. _Documentation Status: http://jikken.readthedocs.io/en/latest/?badge=latest
.. _wiki: https://github.com/outcastofmusic/jikken/wiki
.. _Python Testing with Pytest: https://pragprog.com/book/bopytest/python-testing-with-pytest
.. _Deep Learning with Python: https://www.manning.com/books/deep-learning-with-python
.. _LICENSE: https://github.com/outcastofmusic/jikken/blob/master/LICENSE
.. _tags on this repository: https://github.com/outcastofmusic/jikken/tags

