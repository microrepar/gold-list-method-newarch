import inspect
import os
from typing import Dict, List

from ..core.shared.usecase import UseCase

from ..core import usecases
from ..core.shared.application import Result
from ..core.shared.entity import Entity
from ..external.persistence import repositories
from .viewhelper import GenericViewHelper


class Controller:
    """Controls the flow of all requests made to the system
    """

    def __init__(self):
        self.usecases: Dict[str, UseCase] = usecases
        self.repositories: Dict[str, callable] = repositories
        self.viewhelper = GenericViewHelper()

        # print('>>>>>>>REPO>>>>>>>', self.repositories)
        # print('>>>>>>>USECASES>>>>>>>', self.usecases)

    def __call__(self, request):

        # Stores the request.path uri to retrieve the controller responsible for the requested resource
        uri: str = request.get('resource')
        
        # Retrieves the controller from the request.path uri, if there is no controller for the uri,
        # Returns a default controller that throws an exception for page 404
        usecase = self.usecases.get(uri, self.usecases.get('default'))
        
        # Checks in the usecase.__init__ signature which repository it requires by parameter 
        # and stores it in a list
        repository_signatures = inspect.signature(usecase.__init__)

        # Generates a list of repositories, from the type annotations in the method signature, 
        # __init__ from the UseCase to retrieve the repository name
        repository_classes = [param.annotation for _, param in repository_signatures.parameters.items() \
                   if param.annotation is not inspect.Parameter.empty and inspect.isclass(param.annotation)]

        # Retrieves the class name from the repository that was defined in the __init__ param from the usecase
        repo_name = repository_classes[-1].__name__
        
        # Retrieves the repository by class name
        repository_class = self.repositories.get(repo_name, self.repositories.get('default'))
        repository = repository_class()

        # Check the signature of the use case.execute which entities it requires by parameter 
        # and store in a list
        entity_signatures = inspect.signature(usecase.execute)

        # Generate a list of entities, from the type annotations in the controller signature, 
        # to use in the generic viewhelper
        entity_classes = [param.annotation for _, param in entity_signatures.parameters.items() \
                   if param.annotation is not inspect.Parameter.empty and inspect.isclass(param.annotation)]

        # Passes the request and the list of entities that the controller requires to the generic viewhelper. 
        # Attempts to create the objects requested in the controller parameter.
        entities: List[Entity] = self.viewhelper.get_entities(*entity_classes, request=request)

        # Executes the controller, passing as arguments the objects constructed by the generic viewhelper, 
        # returning the response processed by the application.
        result: Result = usecase(repository=repository).execute(*entities)

        return self.viewhelper.set_view(result, request)
