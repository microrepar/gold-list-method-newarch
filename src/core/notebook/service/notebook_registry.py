from src.core.shared.application import Result
from ...shared.usecase import UseCase
from ..model.notebook import Notebook
from .notebook_repository import NotebookRepository
from src.core import usecase_map


@usecase_map('/notebook/registry')
class NotebookRegistry(UseCase):

    def __init__(self, *, repository: NotebookRepository):
        self.repository = repository

    def execute(self, notebook: Notebook) -> int:
        result = Result()
        result.msg = notebook.validate_data()

        if result.msg:
            result.entidades = notebook
            return result
        
        try:
            new_notebook = self.repository.registry(notebook)
        except Exception as error:
            if 'already exists' in str(error):
                result.msg = f'Notebook name "{notebook.name}" already exists. Choice another name and try again!'
            else:
                result.msg = str(error)
            return result

        result.entidades = new_notebook
        
        return result

        
