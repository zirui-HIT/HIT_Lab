from typing import List
from copy import deepcopy
from utils.phrase import Phrase
from tqdm import tqdm


class Vocabulary(object):
    def __init__(self, storage):
        self.__vocabulary: List[Phrase] = []
        self.__storage = deepcopy(storage)

    def add(self, words: List[str], occ: int):
        """
        向词组表中添加一个词组
        不消重

        :param words: 要添加的词组
        :param occ: 词组出现的次数
        """
        current = Phrase(words, occ)
        self.__storage.add(current)
        self.__vocabulary.append(current)

    def get(self, word: str) -> Phrase:
        """
        从词组表中查询一个单词是否存在
        若存在，则返回相应的词组；否则，返回None

        :param word: 待查询的单词
        """
        ret = self.__storage.get(word)
        if ret is not None:
            return deepcopy(self.__storage.get(word))
        return None

    def load(path: str, max_gram: int, storage):
        """
        从词典文件中加载词组
        词典文件每一行的格式为：
        词组单词个数 词组出现次数 单词1 单词2 ...

        :param path: 词典文件路径
        :param max_gram: 词组单词的最大个数
        :param storage: 词典组织类
        """
        ret = Vocabulary(storage)
        num_file = 0
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                items = line.split()
                if int(items[0]) > max_gram:
                    break
                num_file += 1

        print("loading vocabulary:")
        with open(path, 'r', encoding='utf-8') as f:
            for i, line in tqdm(enumerate(f), total=num_file):
                items = line.split()
                if int(items[0]) > max_gram:
                    break
                ret.add(items[2:], int(items[1]))
        return ret

    def max_length(self):
        """
        返回词典中词组的最大单字长度
        由于采用了枚举查找最大长度，所以尽量减少该方法的调用
        """
        ret = 0
        for phrase in self.__vocabulary:
            ret = max(ret, phrase.length())
        return ret
