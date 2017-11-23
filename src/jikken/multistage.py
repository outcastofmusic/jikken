import json
from collections import OrderedDict

import os

from .experiment import Experiment
from .utils import get_hash

STAGE_METADATA = ".jikken_stage_metadata.json"


def load_stage_metadata(path: str) -> dict:
    """Load the stage metadata from file"""
    assert isinstance(path, str), "path {} is not string".format(path)
    assert os.path.exists(os.path.dirname(path)), "path {} does not exist".format(path)
    file_path = path if path.endswith(STAGE_METADATA) else os.path.join(path, STAGE_METADATA)
    with open(file_path) as file_handle:
        metadata = json.load(file_handle)
    return metadata


def save_stage_metadata(path: str, metadata: dict) -> None:
    """Save stage metadata to file"""
    file_path = path if path.endswith(STAGE_METADATA) else os.path.join(path, STAGE_METADATA)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as file_handle:
        json.dump(metadata, file_handle)


class MultiStageExperiment:
    @classmethod
    def from_dict(cls, doc):

        mse = cls(name=doc['name'])
        mse._experiments = OrderedDict()
        last_step_hash = ''
        for (key, value) in doc["experiments"]:
            last_step_hash = mse.add(Experiment.from_dict(value),
                                     stage_name=key,
                                     last_step_hash=last_step_hash)
        mse._id = doc['id']
        return mse

    def __init__(self, name: str):
        self._name = name
        self._experiments = OrderedDict()
        self._hashes = {}
        self._id = None

    def __repr__(self):
        return "MultiStage {name}:{hash} with steps: {steps}".format(
            name=self._name,
            hash=self.hash(),
            steps=[{key: value} for key, value in self._experiments.items()]
        )

    def add(self, experiment: Experiment, stage_name: str, last_step_hash: str = '') -> str:
        if len(self._experiments) > 0 and last_step_hash != self.hash():
            raise ValueError("last step hash was: {} instead of {}".format(self.hash(), last_step_hash))
        self._experiments[stage_name] = experiment
        self._hashes[stage_name] = self.step_hash_key(stage_name)
        return self.hash()

    def __iter__(self):
        for key, item in self._experiments.items():
            yield key, item

    @property
    def stages(self):
        return [key for key in self._experiments.keys()]

    @property
    def last_stage(self) -> str:
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
            return get_hash(self._hashes[self.last_stage])
        elif step in self._experiments.keys():
            return get_hash(self._hashes[step])
        else:
            raise ValueError("step {} is not in multistage".format(step))

    def __hash__(self):
        return self._hashes[self.last_stage]

    def __eq__(self, other):
        return hash(self) == hash(other)

    def export_metadata(self, directory, exp_id=None):
        """Export metadata to file"""
        metadata = {"multistage_name": self._name,
                    "steps": [key for key in self._experiments.keys()],
                    "id": self._id,
                    "hash": self.hash()}
        # save the doc ids to the metadata
        metadata["exp_ids"] = [self._experiments[steps].doc_id for steps in metadata['steps']]
        if exp_id is not None:
            metadata["exp_ids"][-1] = exp_id
        save_stage_metadata(directory, metadata=metadata)

    def to_dict(self):
        return {
            "name": self._name,
            "hash": self.hash(),
            "experiments": [(key, item.to_dict()) for key, item in self._experiments.items()],
            "steps": [key for key in self._experiments.keys()],
            "type": "multistage",
            "id": self._id
        }

    @property
    def doc_id(self):
        return self._id
