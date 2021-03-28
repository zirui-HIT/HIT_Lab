from typing import List
from copy import deepcopy


class Phrase(object):
    def __init__(self, words: List[str], occ: int):
        """
        表示一个词组

        :param words: 词组
        :paran occ: 词组出现的次数，若为临时使用，请设为0
        """
        self.__words = deepcopy(words)
        self.__occ = occ

    def words(self):
        """
        将存储的词组以List[str]的形式返回
        """
        return deepcopy(self.__words)

    def phrase(self, sep=''):
        """
        将存储的词组以单个string的形式返回

        :param sep: 分隔符
        """
        ret: str = ""
        length = len(self.__words)
        for i in range(length):
            ret = ret + self.__words[i]
            if i != length - 1:
                ret = ret + sep
        return ret

    def occ(self):
        """
        返回该词组出现的次数
        """
        return self.__occ

    def length(self):
        """
        返回组成词组的字的个数
        """
        return len(self.phrase())

    def gram(self):
        """
        返回组成词组的单词的个数
        """
        return len(self.__words)
