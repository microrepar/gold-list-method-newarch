"""core module
"""

from typing import Generic

from .shared.application import Result
from .shared.usecase import I, T, UseCase


class UsecaseNotFoundError(UseCase):

    def __init__(self, repository: Generic[T]):
        self.execute(repository)
    
    def execute(self, entidade: Generic[I]=None) -> Result:
        result = Result()
        result.msg = 'Resource was not found.'
        return result


usecases = {'default': UsecaseNotFoundError}


def usecase_map(resource=None):
    def wrapper(cls):
        usecases.update({resource: cls})
        return cls
    return wrapper


from .notebook.service import notebook_all, notebook_registry, notebook_remove, notebook_by_id
from .pagesection.service import pagesection_get_all, pagesection_registry
# from .sentence.service import sentence_get_all, sentence_registry
