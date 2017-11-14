=====
Usage
=====

Usage Example
-------------

The main goal of *Jikken* is to require as little changes to your experiment code as possible. It's main assumption is that you have a script that runs an experiment and that
the scripts accepts at least a positional argument with the location of the experiment's config.
e.g. Let's assume you have an experiment runs by running my_experiment.py and it reads its configuration from a yaml file myconfig.yaml you would run it with:  ::


    python my_experiment.py myconfig.yaml

Then in order to let jikken record the experiment you would run instead: ::

    jikken run my_experiment.py -c myconfig.yaml -n "my first experiment"

Jikken will then capture the config, Start the experiment, capture stdout and stderr, and save the information in the database as set in the config file.


Running an Experiment
----------------------

Using a reference config
^^^^^^^^^^^^^^^^^^^^^^^^

Monitoring Variables
^^^^^^^^^^^^^^^^^^^^


Retrieving Experiments from the database
-----------------------------------------


Running Multistage Experiments
-------------------------------

