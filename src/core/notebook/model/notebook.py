import datetime
from typing import List


from ...shared.utils import date_to_string


class Notebook:
    def __init__(self, *,
                 name              : str=None,
                 id_               : int=None,
                 created_at        : datetime.date=None,
                 updated_at        : datetime.date=None,
                 list_size         : int=None,
                 days_period       : int=None,
                 page_section_list : List['PageSection']=list(),
                 foreign_idiom     : str=None,
                 mother_idiom      : str=None):
        
        self.name              = name
        self.id                = id_
        self.created_at        = created_at
        self.updated_at        = updated_at
        self.list_size         = list_size
        self.days_period       = days_period
        self.page_section_list = page_section_list
        self.foreign_idiom     = foreign_idiom
        self.mother_idiom      = mother_idiom

    def validate_data(self) -> List[str]:
        
        msg  = list()
        if not self.name or self.name.strip() == '':
            msg.append(
                'Field "name" cannot empty or filled with white spaces.'
            )
        if not self.foreign_idiom or self.foreign_idiom.strip() == '':
            msg.append(
                'Field "foreign idiom" cannot empty or filled with white spaces.'
            )
        if not self.mother_idiom or self.mother_idiom.strip() == '':
            msg.append(
                'Field "mother idiom" cannot empty or filled with white spaces.'
            )
        return msg

    def data_to_dataframe(self):
        return [
            {
                'id'            : self.id,
                'name'          : self.name,
                'created_at'    : self.created_at,
                'updated_at'    : self.updated_at,
                'list_size'     : self.list_size,
                'days_period'   : self.days_period,
                'foreign_idiom' : self.foreign_idiom,
                'mother_idiom'  : self.mother_idiom,
            }
        ]
    
    def data_to_redis(self):
        return {
                'id'            : self.id,
                'name'          : self.name,
                'created_at'    : date_to_string(self.created_at),
                'updated_at'    : date_to_string(self.updated_at),
                'list_size'     : self.list_size,
                'days_period'   : self.days_period,
                'foreign_idiom' : self.foreign_idiom,
                'mother_idiom'  : self.mother_idiom
            }
    
    def __str__(self) -> str:
        return (f'{self.__class__.__name__}'
                f'('
                    f'id={self.id}, '
                    f'name="{self.name}", '
                    f'list_size={self.list_size}, '
                    f'days_period={self.days_period}, '
                    f'foreign_idiom={self.foreign_idiom}, '
                    f'mother_idiom={self.mother_idiom}'
                ')'
        )
    
    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}'
                f'('
                    f'id={self.id}, '
                    f'name="{self.name}", '
                    f'list_size={self.list_size}, '
                    f'days_period={self.days_period}, '
                    f'foreign_idiom={self.foreign_idiom}, '
                    f'mother_idiom={self.mother_idiom}'
                ')'
        )
    
    def get_page_section(self, *, distillation_at, group) -> 'PageSection':
        for page_section in self.page_section_list:
            if distillation_at == page_section.distillation_at \
                    and group == page_section.group \
                        and page_section.created_at is not None:
                return page_section
    
    def count_page_section_by_group(self, *, group):
       return len([p for p in self.page_section_list if p.group.value == group.value and not p.created_at != p.distillation_at])

