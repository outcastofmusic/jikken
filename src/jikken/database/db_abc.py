from abc import ABCMeta, abstractmethod
from typing import Any

from .database import ExperimentQuery, MultiStageExperimentQuery

from enum import Enum


class ExperimentType(Enum):
    Experiment = "experiment"
    MultiStageExperiment = "multistage"


class DB(metaclass=ABCMeta):
    @abstractmethod
    def stop_db(self):
        pass

    @abstractmethod
    def add(self, doc: dict) -> int:
        pass

    @abstractmethod
    def get(self, doc_id: int, collection: str) -> dict:
        pass

    @abstractmethod
    def list_experiments(self, query: ExperimentQuery) -> dict:
        pass

    @abstractmethod
    def list_ms_experiments(self, query: MultiStageExperimentQuery) -> dict:
        pass
    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def update(self, experiment_id: int, experiment: dict) -> None:
        pass

    @abstractmethod
    def update_key(self, experiment_id: int, value: Any, key: str, mode='set') -> None:
        pass

    @abstractmethod
    def delete(self, experiment_id: int) -> None:
        pass

    @abstractmethod
    def delete_all(self) -> None:
        pass

    @property
    def collections(self):
        return ["experiment", "multistage"]
