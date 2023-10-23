from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.pagesection import PageSection
from .pagesection_repository import PageSectionRepository


@usecase_map('pagesection/get_sentences_by_group')
class GetSentencesByGroup(UseCase):

    def __init__(self, repository: PageSectionRepository):
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        result = Result()

        try:
            pagesection_list = self.repository.find_by_field(entity=entity)
            sentence_list = []
            for page in pagesection_list:
                sentence_list.extend(page.sentences)

            if len(sentence_list) < 1:
                result.msg = 'There are no sentences to insert automaticly'
            
            result.entities = sentence_list
            return result

        except Exception as error:
            result.msg = str(error)
            result.entities = entity
            return result