import json
from collections import OrderedDict

import os

from .experiment import Experiment
from .utils import get_hash


class Pipeline:
    def __init__(self, name: str):
        self._name = name
        self._experiments = OrderedDict()
        self._hashes = {}

    def __repr__(self):
        return "Pipeline {name}:{hash} with steps: {steps}".format(
            name=self._name,
            hash=self.hash(),
            steps=[{key: value} for key, value in self._experiments.items()]
        )

    def add(self, experiment: Experiment, step_name: str, last_step_hash: str) -> str:
        if len(self._experiments) > 0 and last_step_hash != self.hash():
            raise ValueError("last step hash was: {} instead of {}".format(self.hash(), last_step_hash))
        self._experiments[step_name] = experiment
        self._hashes[step_name] = self.step_hash_key(step_name)
        return self.hash()

    def __iter__(self):
        for key, item in self._experiments.items():
            yield key, item

    @property
    def last_step(self) -> str:
        return next(reversed(self._experiments))

    def step_index(self, step):
        for index, step_name in enumerate(self._experiments.keys()):
            if step_name == step:
                return index
        else:
            return -1

    def step_hash_key(self, step):
        hash_key = hash(self._name)
        for key, item in self._experiments.items():
            hash_key = hash(hash_key) ^ hash(key) ^ hash(item)
            if key == step:
                break
        return hash_key

    def hash(self, step=None):
        if step is None:
            return get_hash(str(self._hashes[self.last_step]))
        elif step in self._experiments.keys():
            return get_hash(str(self._hashes[step]))
        else:
            raise ValueError("step {} is not in Pipeline".format(step))

    def __hash__(self):
        return self._hashes[self.last_step]

    def __eq__(self, other):
        return hash(self) == hash(other)

    def export_metadata(self, directory):
        assert os.path.isdir(directory)
        with open(os.path.join(directory, ".jikken_config.json")) as file_handle:
            metadata = {"pipeline_name": self._name,
                        "steps": [key for key in self._experiments.keys()],
                        "hash": self.hash()}
            json.dump(metadata, file_handle)

    def to_dict(self):
        return {
            "name": self._name,
            "hash": self.hash(),
            "experiments": [{key: item.to_dict()} for key, item in self._experiments.items()]
        }
