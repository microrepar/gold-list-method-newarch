from typing import List

from src.core.notebook import Notebook, NotebookRepository

from .model.base import NotebookModel
from .settings.connection import DBConnectionHandler
from ...persistence import repository_map


@repository_map
class SqlAlchemyNotebookRepository(NotebookRepository):
    """SqlAlchemy implementation of NotebookRepository"""

    def __init__(self):
        self.database = DBConnectionHandler()

    def get_all(self) -> List[Notebook]:
        instance_list = self.database.session.query(NotebookModel).all()
        entity_list = []
        for instance in instance_list:
            entity_list.append(
                NotebookModel.notebook_model_to_entity(instance)
            )
        self.database.close()
        return entity_list 


    def registry(self, entity: Notebook) -> None:
        instance = NotebookModel.notebook_entity_to_model(entity)
        try:
            self.database.session.add(instance)
            self.database.session.commit()
            return NotebookModel.notebook_model_to_entity(instance)
        except Exception as error:
            self.database.session.rollback()
            raise error
        finally:
            self.database.close()
