from copy import deepcopy
from utils.phrase import Phrase


class HashBucket(object):
    def __init__(self, seed: int = 131, mod: int = 0xFFFFF):
        self.__seed = seed
        self.__mod = mod
        self.__bucket = []
        for i in range(mod + 1):
            self.__bucket.append([])

    def add(self, phrase: Phrase):
        """
        向线性表中添加一个词组

        :param phrase: 待添加词组
        """
        self.__bucket[self.__BKDR_hash(phrase.phrase())].append(phrase)

    def get(self, phrase: str) -> Phrase:
        """
        查询哈希桶中某个词组是否存在
        若不存在，返回None；否则，返回相应的Phrase

        :param phrase: 待查询词组
        """
        value = self.__BKDR_hash(phrase)
        for s in self.__bucket[value]:
            if s.phrase() == phrase:
                return deepcopy(s)
        return None

    def __digit(self, character) -> int:
        """
        将一个汉字转化为数字

        :param character: 待转化的汉字
        """
        byte = character.encode('GBK')
        if len(byte) == 1:
            return byte[0]
        return (byte[0] - 0x81) * 190 + (byte[1] - 0x40) - (byte[1] // 128)

    def __BKDR_hash(self, phrase: str) -> int:
        """
        计算一个词组的BKDR哈希值

        :param phrase: 待哈希的词组
        """
        ret = 0
        for c in phrase:
            ret = ret * self.__seed + self.__digit(c)
        return ret & self.__mod
