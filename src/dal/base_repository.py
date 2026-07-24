# base_repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base defining the CRUD contract every repository must implement."""

    @abstractmethod
    def save(self, entity: T) -> T:
        """Persist a new entity and return it with its assigned id."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, entity_id: int) -> T | None:
        """Fetch a single entity by id, or None if not found."""
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> list[T]:
        """Fetch all entities."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        """Delete an entity by id."""
        raise NotImplementedError