import datetime
from ...shared.application import Result

from ...shared.usecase import UseCase
from ..model.pagesection import PageSection, Group
from .pagesection_repository import PageSectionRepository
from ....core import usecase_map


@usecase_map('/pagesection/registry')
class PageSectionRegistry(UseCase):

    def __init__(self, repository: PageSectionRepository):
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        result = Result()

        entity_filter = PageSection(created_at=entity.created_at,
                                    group=entity.group,
                                    notebook=entity.notebook)

        has_pagesection = self.repository.find_by_field(entity_filter)

        if has_pagesection:
            result.msg = (f'Headlist cannot be registred because '
                          f'there is a headlist created at same date {entity.created_at}.')

        next_page_number = self.repository.get_last_page_number(entity)
        entity.page_number = next_page_number
        entity.set_distillation_at()
        
        result.msg = entity.validate_data()

        if result.qtde_msg() > 0:
            result.entidades = entity
            return result        

        try:
            new_entity = self.repository.registry(entity=entity)
            result.entidades = new_entity

            if entity.group == Group.A:
                clone_entity = entity.clone()
                clone_entity.distillation_at = entity.created_at
                clone_entity.distillated = True
                self.repository.registry(entity=clone_entity)

        except Exception as error:
            result.msg = str(error)
            result.entidades = entity
            return result        

        return result