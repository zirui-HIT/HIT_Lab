from typing import List
from utils.phrase import Phrase
from copy import deepcopy


class LinearList(object):
    def __init__(self):
        self.__dictionary: List[Phrase] = []

    def add(self, phrase: Phrase):
        """
        向线性表中添加一个词组

        :param phrase: 待添加词组
        """
        self.__dictionary.append(phrase)

    def get(self, phrase: str) -> Phrase:
        """
        查询线性表中某个词组是否存在，若不存在，返回None；否则，返回相应的Phrase

        :param phrase: 待查询词组
        """
        for p in self.__dictionary:
            if p.phrase() == phrase:
                return deepcopy(p)
        return None
