from copy import deepcopy
from utils.phrase import Phrase
from typing import List


class BinaryLinearList(object):
    def __init__(self, max_gram: int):
        """
        使用二分查找的线性表词典结构
        要求插入词组的顺序按照字典序升序
        """
        self.__dictionary: List[List[Phrase]] = []
        self.__gram = 0
        for i in range(max_gram):
            self.__dictionary.append([])

    def add(self, phrase: Phrase):
        """
        向线性表中添加一个词组

        :param phrase: 待添加词组
        """
        self.__dictionary[phrase.gram() - 1].append(phrase)
        self.__gram = max(self.__gram, phrase.gram())

    def get(self, phrase: str) -> Phrase:
        """
        二分查询线性表中某个词组是否存在
        若不存在，返回None；否则，返回相应的Phrase

        :param phrase: 待查询词组
        """
        for i in range(self.__gram):
            L = 0
            R = len(self.__dictionary[i])
            M = (L + R) >> 1
            while L <= R:
                if self.__dictionary[i][M].phrase() == phrase:
                    return deepcopy(self.__dictionary[i][M])
                elif self.__dictionary[i][M].phrase() < phrase:
                    L = M + 1
                else:
                    R = M - 1
                M = (L + R) >> 1
            if self.__dictionary[i][M].phrase() == phrase:
                return deepcopy(self.__dictionary[i][M])
        return None
