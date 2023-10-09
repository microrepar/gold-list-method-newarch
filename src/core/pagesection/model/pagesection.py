import datetime
from enum import Enum
from typing import List

from ...notebook import Notebook
from ...sentence.model.sentence import Sentence
from ...shared.entity import Entity
from ...shared.utils import date_to_string


class Group(Enum):
    HEADLIST = 'A'
    A        = 'A'
    B        = 'B'
    C        = 'C'
    D        = 'D'
    NEW_PAGE = 'NP'


class PageSection(Entity):
    def __init__(self, *,
                 id_                  : int=None,
                 notebook             : Notebook=None,
                 section_number       : int=None,
                 page_number          : int=None,
                 group                : Group=None,
                 created_at           : datetime.date=None,
                 created_by           : int=None,
                 distillation_at      : datetime.date=None,
                 distillation_actual  : datetime.date=None,
                 distillated          : bool=False,
                 sentences            : List[Sentence]=[],
                 translated_sentences : List[str]=[],
                 memorializeds        : List[bool]=[]):
        self.id                    = id_
        self.section_number        = section_number
        self.page_number           = page_number
        self.group:Group           = group
        self.created_at            = created_at
        self.distillation_at       = distillation_at
        self._distillated          = distillated
        self.sentences             = sentences
        self.translated_sentences  = translated_sentences
        self.memorializeds         = memorializeds
        self.notebook              = notebook
        self._distillation_actual  = distillation_actual
        self.created_by            = created_by
        self.set_created_by(created_by)        # section_number from  PageSection
    
    def clone(self):
        return self.__class__(
            id_=None,
            section_number=self.section_number,
            page_number=self.page_number,
            group=self.group,
            created_at=self.created_at,
            created_by=self.created_by,
            distillation_at=self.distillation_at,
            distillation_actual=self._distillation_actual,
            distillated=self._distillated,
            sentences=self.sentences,
            translated_sentences=self.translated_sentences,
            memorializeds=self.memorializeds,
            notebook=self.notebook
        )
    
    @property
    def distillated(self):
        return bool(self._distillated)

    @distillated.setter
    def distillated(self, value: bool) :
        self._distillated = bool(value)
        if value:
            self._distillation_actual = datetime.datetime.now().date()

    def set_id(self, id_):
        self.id = id_

    def set_created_by(self, page_section: 'PageSection'=None):
        if isinstance(page_section, PageSection):
            self.created_by = page_section
        else:
            self.created_by = None
        
    def __str__(self):
        group = {
            'A'  : 'HeadList',
            'B'  : 'Group B List',
            'C'  : 'Group C List',
            'D'  : 'Group D List',
            'NP' : 'Group NP List'
        }
        notebook_value = self.notebook.name if isinstance(self.notebook, Notebook) else ''
        return (f'{group.get(self.group.value)} Page {self.page_number} of {self.created_at} with '
                f'distillation date of {self.distillation_at} from the {notebook_value} notebook') if self.group != Group.NEW_PAGE \
                else f'{group.get(self.group.value)} of {self.created_at} will be able to composite a new HeadList.'
        
    def __repr__(self):
        created_by_id = None
        if self.created_by is not None:
            created_by_id = self.created_by.section_number
        notebook_id = None
        if self.notebook is not None:
            notebook_id = self.notebook.id
        return (f'PageSection('
                    f'id_= {self.id}, '
                    f'section_number={self.section_number}, '
                    f'page_number={self.page_number}, '
                    f'created_at={self.created_at}, '
                    f'created_by_id={created_by_id}, '
                    f'notebook_id={notebook_id}, '
                    f'group="{self.group}", '
                    f'translated_sentences={self.translated_sentences}, '
                    f'memorializeds={self.memorializeds}, '
                    f'distillation_at={self.distillation_at}, '
                    f'distillated={self.distillated}'
                ')'
        )
    
    def get_distillation_event(self):
        if self.distillated:
            color = {'A'  : '#9B9B9B',
                     'B'  : '#9B9B9B',
                     'H'  : '#9B9B9B',
                     'C'  : '#9B9B9B',
                     'D'  : '#9B9B9B',
                     'NP' : '#9B9B9B'}
        else:
            color = {'A'  : '#FF0000',
                     'B'  : '#00A81D',
                     'C'  : '#002BFF',
                     'D'  : '#B300B7',
                     'NP' : '#000000'}
        sequence = {'A'  : '1st',
                    'B'  : '2nd',
                    'C'  : '3rd',
                    'D'  : '4th',
                    'NP' : '🔁'}
        
        return {
            "title"      : f"{sequence.get(self.group.value, 'Indef')} Distill {self.group.value}" if self.created_at \
                            else f" Add HeadList",
            "color"      : color.get(self.group.value, color['NP']) if self.created_at \
                            else '#DCDCDC',
            "start"      : f"{self.distillation_at}",
            "end"        : f"{self.distillation_at}",
            "resourceId" : f"{self.group.value.lower()}",
        }

    def data_to_dataframe(self):
        created_by = None
        if self.created_by is not None:
            created_by = self.created_by.page_number
        return {    
            'id'                   : [i for i in range(self.id, self.id + len(self.sentences))],
            # 'section_number'       : [self.section_number for _ in range(len(self.sentences))],
            'page_number'          : [self.page_number for _ in range(len(self.sentences))],
            'group'                : [self.group.value for _ in range(len(self.sentences))],
            'created_at'           : [self.created_at for _ in range(len(self.sentences))],
            'created_by_id'        : [created_by for _ in range(len(self.sentences))],
            'distillation_at'      : [self.distillation_at for _ in range(len(self.sentences))],
            'distillation_actual'  : [self._distillation_actual for _ in range(len(self.sentences))],
            'distillated'          : [self._distillated for _ in range(len(self.sentences))],
            'notebook_id'          : [self.notebook.id for _ in range(len(self.sentences))],
            'sentence_id'          : [v.id for v in self.sentences],
            'translated_sentences' : [v for v in self.translated_sentences],
            'memorized'            : [v for v in self.memorializeds],
        }
    
    def data_to_redis(self):
        created_by = None
        if self.created_by is not None:
            created_by = self.created_by.page_number
        return {    
            'id'                  : self.id,
            'section_number'      : self.section_number,
            'page_number'         : self.page_number,
            'group'               : self.group.value,
            'created_at'          : date_to_string(self.created_at),
            'created_by_id'       : created_by,
            'distillation_at'     : date_to_string(self.distillation_at),
            'distillation_actual' : date_to_string(self._distillation_actual),
            'distillated'         : self._distillated,
            'notebook_id'         : self.notebook.id,
            'sentences_id'        : [s.id for s in self.sentences],
            'translated_sentence' : self.translated_sentences,
            'memorized'           : self.memorializeds,
        }

    def validate_data(self):
        if self.notebook is None or self.notebook.days_period is None:
            return f'Notebook is none or it has not defined days_period attribute value.'

        self.distillation_at = (self.created_at + datetime.timedelta(days=self.notebook.days_period))
                