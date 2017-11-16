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

The subcommand to run experiments is `run`. If we type: ::

        jikken run -h

we get the following information about the command: ::

Usage: jikken run [OPTIONS] SCRIPT_PATH

  run a single stage experiment from a script. e.g. jikken run script.py -c
    config.yaml

    Options:
      -c, --configuration_path PATH  A file or a directory with files that hold
                                     the variables that define the experiment
                                     [required]
      -n, --name TEXT                the experiment name  [required]
      -r, --ref_path PATH            A file or a directory with files that hold
                                     the variables that define the experiment
      -a, --args TEXT                extra arguments that can be passed to the
                                     script multiple can be added,e.g. -a a=2 -a
                                     batch_size=63 -a early_stopping=False
      -t, --tags TEXT                tags that can be used to distinguish the
                                     experiment inside the database. Multiple can
                                     be added e.g. -t org_name -t small_data -t
                                     model_1
      -h, --help                     Show this message and exit.


`jikken run` expects a positional argument which is the path of the script to run and a number of options.
All options have both a short form and a long form.

Besides the script path  two options are required.
The first one is `-c`, `--configuration_path` and should be followed by the path to the configuration for the experiment. This can be either the path to a `.json` or `.yaml` file or the path to a directory holding multiple files. The files in the directory can be organized as subfolders. Of course as explained above this path will be passed as positional input to the script itself, and the script should be able to use it.
The second required option is `-n`, `--name`. Itt should be a small name way to identify the experiment to be run. It doesn't have to be unique. Multiple words can be used e.g. ``-n "my first nlp experiment"`` and can later be retrieved from the db  by searching for part of the name.

Optionally  the `-t`, `--tag` option can be used to add tags to the experiment. Multiple tags can be added to an experiment e.g. ::

    jikken run my_experiment.py -c myconfig.yaml -n "my first experiment" -t nlp -t tensorflow -t kaggle_data

Tags are pivotal for distinguishing between experiments and their generous use is recommended.

In case the script expects more keyword arguments the `-a`, `--args` option can be used  to pass them. These will also be stored in the database as parts of the variables used. e.g ::

    jikken run my_experiment.py -c myconfig.yaml -n "my first experiment" -a batch_size=15 -a early_stopping=False

Extra positional arguments are currently not supported.

Using a reference config
^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes you have some reference configuration and you just want to change one or two options. The `-r`, `--ref_path` option allows you to do that. When `-r` option is used, whatever's afterward is used as the reference and what is afterh the `-c` option will be used to update the reference variables. The structure for the update variables must match the structure of the reference variables, but only the variables that will be updated need to inside the `-r` path. e.g. ::


    jikken run my_experiment.py -c update_config.yaml -r myconfig.yaml -n "my first experiment"

where myconfig.yaml could be ::

        model_parameters:
           num_layers: 10
           hidden_size: 50
           optimizer: Adam
        input_parameters:
           batch_size: 128
           augment: true

and then update_config.yaml need only be ::

        model_parameters:
           optimizer: SGD
        input_parameters:
           batch_size: 64

Similarly if `-r` is a directory, then `-c` must also be a directory with the sub.


Monitoring Variables
^^^^^^^^^^^^^^^^^^^^


Retrieving Experiments from the database
-----------------------------------------


Running Multistage Experiments
-------------------------------

