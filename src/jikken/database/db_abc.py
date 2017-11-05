from abc import ABCMeta, abstractmethod
from typing import Any


class DB(metaclass=ABCMeta):
    @abstractmethod
    def stop_db(self):
        pass

    @abstractmethod
    def add(self, experiment: dict) -> int:
        pass

    @abstractmethod
    def get(self, experiment_id: int) -> dict:
        pass

    @abstractmethod
    def list_experiments(self, ids: list = None, tags: list = None, query_type: str = "and") -> dict:
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
