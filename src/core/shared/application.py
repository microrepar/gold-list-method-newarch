"""Módulo aplicacao - contém as classes da aplicação
"""
from typing import List
from collections.abc import Sequence


list_entidade = List[object]
list_str = List[str]


class Result:

    def __init__(self):
        self.__msg = list()
        self.__entidades: list_entidade = list()
        self.form = None

    @property
    def msg(self) -> list_str:
        return self.__msg

    @msg.setter
    def msg(self, mensagem: str):
        if isinstance(mensagem, str):
            self.__msg += list([mensagem])
        elif isinstance(mensagem, Sequence):
            self.__msg += list(mensagem)

    @property
    def entidades(self) -> list_entidade:
        return self.__entidades

    @entidades.setter
    def entidades(self, entidade):
        if isinstance(entidade, Sequence):
            self.__entidades += list(entidade)
        elif entidade is not None:
            self.__entidades += list([entidade])

    def qtde_entidades(self):
        return len(self.entidades)

    def qtde_msg(self):
        return len(self.msg)
    
    def to_dict(self):
        return {
            'messages': self.__msg,
            'entities': self.__entidades,
        }