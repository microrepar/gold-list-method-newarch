from abc import abstractmethod
from typing import List, Protocol, runtime_checkable

from ..model.sentence import Sentence


@runtime_checkable
class SentenceRepository(Protocol):

    @abstractmethod
    def registry(self, entity: Sentence, clone_entity: Sentence) -> None :
        """Registry a Sentence into database 
        """

    @abstractmethod
    def get_all(self, entity: Sentence = None) -> List[Sentence]:
        """Get all registred Sentences in database
        """

    @abstractmethod
    def get_by_id(self, entity: Sentence) -> Sentence:
        """Get by id a registred Sentence in database
        """