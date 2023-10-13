from ...shared.application import Result

from ...shared.usecase import UseCase
from ..model.pagesection import PageSection, Group
from .pagesection_repository import PageSectionRepository
from ....core import usecase_map

NEXT_GROUP = {
    'A': Group.B,
    'B': Group.C,
    'C': Group.D,
    'D': Group.NEW_PAGE,
}


@usecase_map('/pagesection/distillation')
class PageSectionDistillation(UseCase):

    def __init__(self, repository: PageSectionRepository):
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        
        result = Result()

        entity_clone = entity.clone()        
        entity_clone.sentences = [entity.sentences[i] for i, m in enumerate(entity.memorializeds) if m is False]
        entity_clone.translated_sentences = ['' for _ in entity_clone.sentences]
        entity_clone.memorializeds = [False for _ in entity_clone.sentences]
        entity_clone.group = NEXT_GROUP.get(entity.group.value)
        entity_clone.set_created_by(entity)
        entity_clone.set_distillation_at()
        
        result.msg = entity_clone.validate_data()
        if entity_clone.group is None:
            result.msg = f'Not exists Group {entity.group}'

        entity.distillated = True
        result.msg = entity.validate_data()

        if result.qtde_msg() > 0:
            result.entidades = entity
            return result

        try:
            updated_pagesection = self.repository.update(entity)
            result.entidades = updated_pagesection
            
            new_entity = self.repository.registry(entity_clone)
            
            return result        
        except Exception as error:
            result.msg = str(error)
            entity.distillated = None
            result.entidades = entity
            
        return result        
        