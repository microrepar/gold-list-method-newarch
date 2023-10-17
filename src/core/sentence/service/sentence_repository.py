from abc import abstractmethod
from typing import List, Protocol, runtime_checkable

from src.core.shared.repository import Repository

from ..model.sentence import Sentence


@runtime_checkable
class SentenceRepository(Repository, Protocol):

    @abstractmethod
    def registry(self, entity: Sentence, clone_entity: Sentence) -> Sentence :
        """Registry a Sentence into database 
        """

    @abstractmethod
    def get_all(self, entity: Sentence = None) -> List[Sentence]:
        """Get all registred Sentences in the database
        """

    @abstractmethod
    def get_by_id(self, entity: Sentence) -> Sentence:
        """Get by id a registred Sentence in the database
        """
    
    @abstractmethod
    def find_by_field(self, entity: Sentence) -> Sentence:
        """Get by id a registred Sentence in the database
        """