import datetime
import json
from typing import List

from sqlalchemy import (BigInteger, Boolean, Column, Date, DateTime, Float,
                        ForeignKey, Integer, MetaData, Sequence, String, Table,
                        Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.core.notebook import Notebook
from src.core.pagesection import Group, PageSection
from src.core.sentence import Sentence

Base = declarative_base(metadata=MetaData(schema='gold_list_method'))
metadata = Base.metadata


class NotebookModel(Base):
    __tablename__ = 'notebook'
    __table_args__ = {"schema": "gold_list_method"}

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True)
    created_at = Column(Date, default=datetime.datetime.now)
    updated_at = Column(Date)
    list_size = Column(Integer)
    days_period = Column(Integer)
    foreign_idiom = Column(String(100))
    mother_idiom = Column(String(100))

    page_section_list = relationship('PageSectionModel', back_populates='notebook')
    
    @classmethod
    def notebook_model_to_entity(cls, model: 'NotebookModel'):       
        return Notebook(
            id_=model.id,
            name=model.name,
            created_at=model.created_at,
            updated_at=model.updated_at,
            list_size=model.list_size,
            days_period=model.days_period,
            foreign_idiom=model.foreign_idiom,
            mother_idiom=model.mother_idiom,
        )
    
    @classmethod
    def notebook_entity_to_model(cls, entity: Notebook):
        notebook_model = cls(id=entity.id,
                             name=entity.name,
                             created_at=entity.created_at,
                             updated_at=entity.updated_at,
                             list_size=entity.list_size,
                             days_period=entity.days_period,
                             foreign_idiom=entity.foreign_idiom,
                             mother_idiom=entity.mother_idiom)
        
        return notebook_model
    


##############################################################################

pagesection_sentence_assoc = Table(
    'pagesection_sentence_assoc', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('pagesectio_id', Integer, ForeignKey('page_section.id')),
    Column('sentence_id', Integer, ForeignKey('sentence.id'))
)

##############################################################################


class PageSectionModel(Base):
    __tablename__ = 'page_section'
    __table_args__ = {"schema": "gold_list_method"}

    id = Column(Integer, primary_key=True)
    section_number = Column(Integer)
    page_number = Column(Integer)
    group = Column(String(1))
    created_at = Column(Date)
    distillation_at = Column(Date)
    distillated = Column(Boolean)
    distillation_actual = Column('distillation_actual', Date)
    created_by = Column(Integer)
    _translated_sentences = Column('translated_sentences', String)
    _memorializeds = Column('memorializeds', String)

    notebook_id = Column(Integer, ForeignKey('notebook.id'))
    notebook = relationship('NotebookModel', back_populates='page_section_list')

    sentences = relationship('SentenceModel', secondary=pagesection_sentence_assoc, back_populates='page_sections')

    @property
    def translated_sentences(self) -> List[bool]:
        return json.loads(self._translated_sentences)
    
    @translated_sentences.setter
    def translated_sentences(self, bool_list: List[bool]):
        self._translated_sentences = json.dumps(bool_list)

    @property
    def memorializeds(self):
        return json.loads(self._memorializeds)
    
    @memorializeds.setter
    def memorializeds(self, bool_list: List[bool]):
        self._memorializeds = json.dumps(bool_list)
    
    @classmethod
    def pagesection_model_to_entity(cls, model: 'PageSectionModel') -> PageSection:
        entity = PageSection(
                id_=model.id,
                section_number=model.section_number,
                page_number=model.page_number,                
                created_at=model.created_at,
                created_by=model.created_by,
                distillation_at=model.distillation_at,
                distillation_actual=model.distillation_actual,
                distillated=model.distillated
        )
        entity.group = Group(model.group)
        entity.translated_sentences = model.translated_sentences
        entity.memorializeds = model.memorializeds

        return entity
    
    @classmethod        
    def pagesection_entity_to_model(cls, entity: PageSection) -> 'PageSectionModel':
        model = cls(
            id=entity.id,
            section_number=entity.section_number,
            page_number=entity.page_number,
            group=entity.group.value,
            created_at=entity.created_at,
            created_by=entity.created_by,
            distillation_at=entity.distillation_at,
            distillation_actual=entity._distillation_actual,
            distillated=entity.distillated,
            translated_sentences=entity.translated_sentences,
            memorializeds=entity.memorializeds
        )

        return model



##############################################################################

class SentenceModel(Base):
    __tablename__ = 'sentence'
    __table_args__ = {"schema": "gold_list_method"}

    id = Column(Integer, primary_key=True)
    created_at = Column(Date, default=datetime.datetime.now)
    foreign_language = Column(String)
    mother_tongue = Column(String)
    foreign_idiom = Column(String)
    mother_idiom = Column(String)

    page_sections = relationship('PageSectionModel', secondary=pagesection_sentence_assoc, back_populates='sentences')

    @classmethod
    def sentence_model_to_entity(cls, model: 'SentenceModel') -> Sentence:
        return Sentence(
            id_=model.id,
            created_at=model.created_at,
            foreign_language=model.foreign_language,
            mother_tongue=model.mother_tongue,
            foreign_idiom=model.foreign_idiom,
            mother_idiom=model.mother_idiom
        )
    
    @classmethod        
    def sentence_entity_to_model(cls, entity: PageSection) -> 'SentenceModel':
        return cls(
            id=entity.id,
            created_at=entity.created_at,
            foreign_language=entity.foreign_language,
            mother_tongue=entity.mother_tongue,
            foreign_idiom=entity.foreign_idiom,
            mother_idiom=entity.mother_idiom
        )