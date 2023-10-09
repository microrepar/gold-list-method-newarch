import datetime
from typing import List

from sqlalchemy import and_, func

from src.core.pagesection import PageSection, PageSectionRepository, Group
from src.core.notebook import Notebook
from src.core.sentence import Sentence

from ...persistence import repository_map
from .model.base import NotebookModel, PageSectionModel, SentenceModel
from .settings.connection import DBConnectionHandler


@repository_map
class SqlAlchemyPageSectionRepository(PageSectionRepository):
    """SqlAlchemy implementation of PageSectionRepository"""

    def __init__(self):
        self.database = DBConnectionHandler()

    def get_all(self) -> List[PageSection]:
        try:
            instance_page_list = self.database.session.query(PageSectionModel).all()
            
            entity_page_list = []
                            
            for instance_page in instance_page_list:
                entity: PageSection = None 
                entity = PageSectionModel.pagesection_model_to_entity(instance_page)
                entity.sentences = list()            

                instance_sentence_list = instance_page.sentences
                for instance_sentence in instance_sentence_list:
                    entity_sentence: Sentence = None
                    entity_sentence = SentenceModel.sentence_model_to_entity(instance_sentence)    
                    entity.sentences.append(entity_sentence)
            
                entity_page_list.append(entity)
            return entity_page_list
        
        except Exception as error:
            self.database.session.rollback()
            raise error
        finally:
            self.database.close()


    def get_by_id(self, entity: PageSection) -> PageSection:
        
        try:
            with self.database.session.begin():
                instance = self.database.session.query(PageSectionModel).filter(
                    and_(
                        PageSectionModel.created_at == entity.created_at, 
                        PageSectionModel.distillation_at == entity.created_at,
                        PageSectionModel.group == entity.group.value
                    )
                ).one_or_none()

                if instance:
                    return PageSectionModel.pagesection_model_to_entity(instance)            
                return
                
        except Exception as error:
            self.database.session.rollback()
            return str(error)


    def find_by_field(self, entity: PageSection) -> List[PageSection]:

        filters = dict([v for v in vars(entity).items() if not v[0].startswith('_') and bool(v[-1])])

        kwargs = {}
        for attr, value in filters.items():
            if bool(value) is False: continue

            if isinstance(value, Notebook):
                attr = 'notebook_id'
                value = int(value.id)
            elif isinstance(value, Group):
                value = value.value            
            elif isinstance(value, PageSection):
                attr = 'created_at'
                value = value.created_by.created_at
            elif attr in 'created_at':
                if isinstance(value, datetime.date):
                    value = value
                    # value = pd.to_datetime(value).strftime("%Y-%m-%d")
                elif '#' in value:
                    value = None
            elif attr in 'section_number distillated distillation_at':
                ...
            else:
                raise Exception(f'This field "{attr}" cannot be used to find PageSection objects!')
            
            kwargs[attr] = value

        try:
            with self.database.session.begin():
                    
                instance_page_list = (self.database.session.query(PageSectionModel)
                                    .filter_by(**kwargs).all())

                entity_page_list = []
                        
                for instance_page in instance_page_list:
                    entity: PageSection = None 
                    entity = PageSectionModel.pagesection_model_to_entity(instance_page)
                    entity.sentences = list()            

                    instance_sentence_list = instance_page.sentences
                    for instance_sentence in instance_sentence_list:
                        entity_sentence: Sentence = None
                        entity_sentence = SentenceModel.sentence_model_to_entity(instance_sentence)    
                        entity.sentences.append(entity_sentence)
                
                    entity_page_list.append(entity)

                return entity_page_list

        except Exception as error:
            self.database.session.rollback()
            raise error

    def get_last_page_number(self, entity: PageSection=None) -> int:
        try:
            with self.database.session.begin():

                instance: PageSectionModel = PageSectionModel.pagesection_entity_to_model(entity)

                instance.notebook = None
                instance.sentences = list()

                if instance.page_number is None:
                    next_page_number = (self.database.session.query(func.max(PageSectionModel.page_number))
                                    .filter(PageSectionModel.notebook_id == entity.notebook.id)
                                ).scalar()
                    next_page_number = next_page_number + 1 if next_page_number is not None else 1
                    instance.page_number = next_page_number
                
                return next_page_number
            
        except Exception as error:
            self.database.session.rollback()
            raise error


    def registry(self, entity: PageSection) -> PageSection:
        try:
            instance = None
            with self.database.session.begin():

                has_notebook: NotebookModel = self.database.session.query(NotebookModel).filter_by(id=entity.notebook.id).one_or_none()
                if not has_notebook:
                    raise Exception(f'Notebook id={entity.notebook.id} was not found.' )
                
                instance: PageSectionModel = PageSectionModel.pagesection_entity_to_model(entity)

                instance.notebook = None
                instance.sentences = list()

                for sentence in entity.sentences:
                    has_sentence = (self.database.session.query(SentenceModel)
                                    .filter_by(foreign_language=sentence.foreign_language)
                                    .first())
                    if has_sentence:
                        instance.sentences.append(has_sentence)
                    else:
                        instance.sentences.append(
                            SentenceModel.sentence_entity_to_model(sentence)
                        )
                
                instance.notebook_id = has_notebook.id
                has_notebook.page_section_list.append(instance)
                self.database.session.add(instance)
                

            new_entity = PageSectionModel.pagesection_model_to_entity(instance)
            new_entity.notebook = NotebookModel.notebook_model_to_entity(has_notebook)
            new_entity.sentences = [SentenceModel.sentence_model_to_entity(s) for s in instance.sentences]

            return new_entity
            
        except Exception as error:
            self.database.session.rollback()
            raise error
        finally:
            self.database.close()
