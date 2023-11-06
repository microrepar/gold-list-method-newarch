from typing import List

from src.core import usecase_map
from src.core.shared import UseCase
from src.core.shared.application import Result
from .. import Notebook, NotebookRepository


@usecase_map('/notebook/find_by_field')
class NotebookFindByFieldService(UseCase):

    def __init__(self, *, repository: NotebookRepository):
        self.repository = repository

    def execute(self, entity: Notebook) -> Result:
        result = Result()
        
        notebook_list = self.repository.find_by_field(entity)

        if not notebook_list:
            result.msg = f'There are no registred notebooks to connected user!'
            result.entities = notebook_list
            return result
        
        result.entities = notebook_list
        return result
