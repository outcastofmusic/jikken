import json
from collections import OrderedDict

import os

from .experiment import Experiment
from .utils import get_hash


class Pipeline:
    def __init__(self, name: str):
        self.name = name
        self.experiments = OrderedDict()

    def add(self, experiment: Experiment, step_name: str, last_step_hash: str) -> str:
        if self.hash() == last_step_hash or len(self.experiments) == 0:
            self.experiments[step_name] = experiment
        else:
            raise ValueError("last step hash was: {} instead of {}".format(self.hash(), last_step_hash))
        return self.hash()

    def __iter__(self):
        for key, item in self.experiments.items():
            yield key, item

    @property
    def last_step(self) -> str:
        return next(reversed(self.experiments))

    def hash(self, step=None):
        if step is None or step in self.experiments.keys():
            hash_key = ""
            for key, item in self.experiments.items():
                hash_key = hash_key + key + item.hash
                if step is not None and key == step:
                    break
            return get_hash(hash_key)
        else:
            raise ValueError("step {} is not in Pipeline".format(step))

    def export_metadata(self, directory):
        assert os.path.isdir(directory)
        with open(os.path.join(directory, ".jikken_config.json")) as file_handle:
            metadata = {"pipeline_name": self.name,
                        "steps": [key for key in self.experiments.keys()],
                        "hash": self.hash()}
            json.dump(metadata, file_handle)

    def to_dict(self):
        return {
            "name": self.name,
            "hash": self.hash(),
            "experiments": [{key: item.to_dict()} for key, item in self.experiments]
        }
