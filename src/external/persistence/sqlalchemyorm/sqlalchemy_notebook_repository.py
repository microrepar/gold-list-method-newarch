import datetime
from typing import List

from src.core.notebook import Notebook, NotebookRepository
from src.core.pagesection import PageSection
from src.core.sentence import Sentence

from .model.base import NotebookModel, PageSectionModel, SentenceModel, UserModel
from .settings.connection import DBConnectionHandler
from ...persistence import repository_map


@repository_map
class SqlAlchemyNotebookRepository(NotebookRepository):
    """SqlAlchemy implementation of NotebookRepository"""

    def __init__(self):
        self.database = DBConnectionHandler()

    def get_all(self) -> List[Notebook]:
        try:
            with self.database.session.begin():
                instance_list = self.database.session.query(NotebookModel).all()
                
                entity_notebook_list = []
                for instance in instance_list:
                    entity: Notebook = None
                    entity = NotebookModel.notebook_model_to_entity(instance)
                    entity.page_section_list = list()

                    instance_page_list = instance.page_section_list
                    for instance_page in instance_page_list:
                        entity_page: PageSection = None 
                        entity_page = PageSectionModel.pagesection_model_to_entity(instance_page)
                        entity_page.notebook = entity
                        entity_page.sentences = list()

                        entity.page_section_list.append(entity_page)

                        instance_sentence_list = instance_page.sentences
                        for instance_sentence in instance_sentence_list:
                            entity_sentence = None
                            entity_sentence = SentenceModel.sentence_model_to_entity(instance_sentence)    
                            entity_page.sentences.append(entity_sentence)
                    
                    entity.user = UserModel.user_model_to_entity(instance.user)
                    entity_notebook_list.append(entity)
            
                return entity_notebook_list 
        except Exception as error:
            self.database.session.rollback()
            raise error
            
        finally:
            self.database.close()
         
    
    def get_by_id(self, entity: Notebook) -> Notebook:
        try:
            notebook_id = entity.id

            with self.database.session.begin():
                instance: NotebookModel = self.database.session.query(NotebookModel).filter_by(id=notebook_id).one_or_none()
                    
                if not instance:
                    raise Exception(f'There is no notebook with id={notebook_id}.')
                
                entity_notebook_found = NotebookModel.notebook_model_to_entity(instance)
                entity_notebook_found.user = UserModel.user_model_to_entity(instance.user)
                entity_notebook_found.page_section_list = list()
                    
                for instance_page in instance.page_section_list:
                    entity_page: PageSection = None 
                    entity_page = PageSectionModel.pagesection_model_to_entity(instance_page)
                    entity_page.sentences = list()            

                    instance_sentence_list = instance_page.sentences
                    for instance_sentence in instance_sentence_list:
                        entity_sentence: Sentence = None
                        entity_sentence = SentenceModel.sentence_model_to_entity(instance_sentence)                        
                        entity_page.sentences.append(entity_sentence)
                
                    entity_page.notebook = entity_notebook_found
                    entity_notebook_found.page_section_list.append(entity_page)

                return entity_notebook_found 
            
        except Exception as error:
            self.database.session.rollback()
            raise error
        
        finally:
            self.database.session.close()

    
    def find_by_field(self, entity: Notebook) -> List[Notebook]:
        filters = dict([v for v in vars(entity).items() if not v[0].startswith('_') and bool(v[-1])])

        kwargs = {}
        for attr, value in filters.items():
            if bool(value) is False: continue

            if attr in 'created_at':
                if isinstance(value, datetime.date):
                    value = value
                    # value = pd.to_datetime(value).strftime("%Y-%m-%d")
            elif attr in 'user':
                attr = 'user_id'
                value = value.id
            elif attr in 'id name list_size days_period foreing_idiom mother_idiom':
                ...
            else:
                raise Exception(f'This field "{attr}" cannot be used to find Notebook objects!')
            
            kwargs[attr] = value

        try:
            entity_notebook_list = []
            
            with self.database.session.begin():
                instance_list = self.database.session.query(NotebookModel).filter_by(**kwargs).all()
                
                for instance in instance_list:
                    entity: Notebook = None
                    entity = NotebookModel.notebook_model_to_entity(instance)
                    entity.page_section_list = list()

                    instance_page_list = instance.page_section_list
                    for instance_page in instance_page_list:
                        entity_page: PageSection = None 
                        entity_page = PageSectionModel.pagesection_model_to_entity(instance_page)
                        entity_page.notebook = entity
                        entity_page.sentences = list()

                        entity.page_section_list.append(entity_page)

                        instance_sentence_list = instance_page.sentences
                        for instance_sentence in instance_sentence_list:
                            entity_sentence = None
                            entity_sentence = SentenceModel.sentence_model_to_entity(instance_sentence)    
                            entity_page.sentences.append(entity_sentence)
                    
                    entity.user = UserModel.user_model_to_entity(instance.user)
                    entity_notebook_list.append(entity)
            
            return entity_notebook_list 
        
        except Exception as error:
            self.database.session.rollback()
            raise error
            
        finally:
            self.database.close()         


    def registry(self, entity: Notebook) -> Notebook:
        user_id = entity.user.id
        instance = NotebookModel.notebook_entity_to_model(entity)
        
        try:
            with self.database.session.begin():
                has_user = (self.database.session
                            .query(UserModel)
                            .filter_by(id=user_id)
                            .one_or_none())
                
                if has_user is None:
                    raise Exception(f'There is no User with username={entity.username}')
                
                has_user.notebook_list.append(instance)
                self.database.session.add(instance)                

            return NotebookModel.notebook_model_to_entity(instance)
        except Exception as error:
            self.database.session.rollback()
            raise error
        finally:
            self.database.session.close()
