from typing import List

from src.core.pagesection import PageSection, PageSectionRepository

from .model.base import PageSectionModel
from .settings.connection import DBConnectionHandler
from ...persistence import repository_map


@repository_map
class SqlAlchemyPageSectionRepository(PageSectionRepository):
    """SqlAlchemy implementation of PageSectionRepository"""

    def __init__(self):
        self.database = DBConnectionHandler()

    def get_all(self) -> List[PageSection]:
        instance_list = self.database.session.query(PageSectionModel).all()
        entity_list = []
        for instance in instance_list:
            entity_list.append(
                PageSectionModel.pagesection_model_to_entity(instance)
            )
        self.database.close()
        return entity_list 


    def registry(self, entity: PageSection) -> None:
        pass
        instance = PageSectionModel.pagesection_entity_to_model(entity)
        try:
            self.database.session.add(instance)
            self.database.session.commit()
            return PageSectionModel.PageSection_model_to_entity(instance)
        except Exception as error:
            self.database.session.rollback()
            raise error
        finally:
            self.database.close()
