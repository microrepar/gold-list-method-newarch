from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.notebook import Notebook
from .notebook_repository import NotebookRepository


@usecase_map('/notebook/registry')
class NotebookRegistry(UseCase):

    def __init__(self, *, repository: NotebookRepository):
        self.repository = repository

    def execute(self, notebook: Notebook) -> Result:
        result = Result()
        
        result.msg = notebook.validate_data()
        if result.msg:
            result.entities = notebook
            return result
        
        try:
            new_notebook = self.repository.registry(notebook)
        except Exception as error:
            if 'already exists' in str(error):
                result.msg = f'Notebook name "{notebook.name}" already exists. Choice another name and try again!'
            else:
                result.msg = str(error)
            return result

        result.entities = new_notebook
        
        return result

        
