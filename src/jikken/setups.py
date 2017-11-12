import os


class ExperimentSetup:
    """Configuration Class that holds the inputs for an experiment run"""

    def __init__(self, *, name: str, configuration_path: str, script_path: str, args: list = None, tags: list = None,
                 reference_configuration_path: str = None):
        """
        Args:
            configuration_path (str): The path to the configuration file/dir of the experiment
            script_path (str): The path to the script that will run the experiment
            args (list): Optional, list of strings with extra args not included in the configuration_path to
                 be passed to the script. Expected form is ["arg1=x", "arg2=y", "arg3=z"]
            tags (list): Optional, list of strings with tags that describe the experiment
            reference_configuration_path (str): Optional a path for a reference configuration. If it is given
                the reference_configuration_path defines the experiment and the configuration_path only requires
                the updated variables
        """
        assert os.path.exists(configuration_path), "conf path: {} does not exist".format(configuration_path)
        assert os.path.exists(script_path), "script path: {} does not exist".format(script_path)
        self._conf_path = configuration_path
        self._script_path = script_path
        self._name = name
        self._args = [] if args is None else [argument.split("=") for argument in args]
        self._tags = [] if tags is None else tags[:]
        ref_conf_path = reference_configuration_path
        assert ref_conf_path is None or os.path.exists(ref_conf_path), "ref conf path: {} does not exist".format(
            ref_conf_path)
        self._ref_conf_path = ref_conf_path

    @property
    def name(self):
        return self._name

    @property
    def configuration_path(self):
        return self._conf_path

    @property
    def script_path(self):
        return self._script_path

    @property
    def tags(self):
        return self._tags

    @property
    def reference_configuration_path(self):
        return self._ref_conf_path

    @property
    def args(self):
        return self._args


class MultiStageExperimentSetup(ExperimentSetup):
    """class"""

    def __init__(self, *, name, configuration_path, script_path, output_path, stage_name, input_path=None, args=None,
                 tags=None,
                 reference_configuration_path=None):
        """
        Args:
            name (str): The name of the Multistage Experiment
            configuration_path (str): The path to the configuration file/dir of the experiment
            script_path (str): The path to the script that will run the experiment
            args (list): Optional, list of strings with extra args not included in the configuration_path to
                 be passed to the script. Expected form is ["arg1=x", "arg2=y", "arg3=z"]
            tags (list): Optional, list of strings with tags that describe the experiment
            reference_configuration_path (str): Optional a path for a reference configuration. If it is given
                the reference_configuration_path defines the experiment and the configuration_path only requires
                the updated variables
        """
        super(MultiStageExperimentSetup, self).__init__(
            name=name,
            configuration_path=configuration_path,
            script_path=script_path,
            args=args,
            tags=tags,
            reference_configuration_path=reference_configuration_path
        )

        assert input_path is None or os.path.exists(input_path), "input_path doesn't exist: {}".format(input_path)
        self._input_path = input_path
        self._output_path = output_path
        self._stage_name = stage_name

    @property
    def stage_name(self):
        return self._stage_name

    @property
    def input_path(self):
        return self._input_path

    @property
    def output_path(self):
        return self._output_path
