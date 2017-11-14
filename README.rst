***********
Jikken 実験
***********

.. image:: https://travis-ci.org/outcastofmusic/jikken.svg?branch=master
    :alt: cli_status

**Jikken**  is a lightweight cli experiment manager for scientific experiments written in python.

It makes very few assumptions on the experiment and requires almost zero code changes
to the scripts. In fact the only assumption is that the main function of the script to be run
accepts a positional argument with either a directory with json/yaml config files
or a path to single json/yaml file. That's it. Optionally if the code of the
experiment is in a git repo, the git info will be added as well.

Features
########

- Python 3.{5,6} code
- Support for TinyDB, MongoDB, and ES (to be implemented)
- tagging of experiments
- CLI to access experiment data
- only requires the script to load the variables from a file or folder
- support for json/yaml configs
- understands git directories

Getting Started
###############



Contributing
------------

1. Fork it (<https://github.com/yourname/yourproject/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request


Release History
----------------

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

* Brian Okken and his great book on python testing: `Python Testing with Pytest`_.
* Francois Chollet and his book `Deep Learning with Python`_.


.. _cli status: https://travis-ci.org/outcastofmusic/jikken.svg?branch=master
.. _wiki: https://github.com/outcastofmusic/jikken/wiki
.. _Python Testing with Pytest: https://pragprog.com/book/bopytest/python-testing-with-pytest
.. _Deep Learning with Python: https://www.manning.com/books/deep-learning-with-python
.. _LICENSE: https://github.com/outcastofmusic/jikken/blob/master/LICENSE
.. _tags on this repository: https://github.com/outcastofmusic/jikken/tags


