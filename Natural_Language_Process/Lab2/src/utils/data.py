from ordered_set import OrderedSet
from collections import OrderedDict
from typing import List
from copy import deepcopy

import torch.utils.data as Data


class Vocabulary(object):
    def __init__(self):
        """
        vocabulary that store words to be used
        """
        self.__cnt = 0
        self.__index2word = OrderedSet()
        self.__word2index = OrderedDict()

    def add(self, word: str):
        """
        add a word to vocabulary

        :param word: word to add
        """
        if word not in self.__index2word:
            self.__index2word.add(word)
            self.__word2index[word] = self.__cnt
            self.__cnt += 1

    def index2word(self, index: List[List[int]]) -> List[List[str]]:
        """
        get word from vocabulary with index
        index == 0 is padding

        :param index: index of word to get
        """
        ret = []
        for i in range(len(index)):
            word = []
            for j in range(len(index[i])):
                word.append(self.__index2word[index[i][j]])
            ret.append(word)
        return ret

    def word2index(self, word: List[List[str]]) -> List[List[int]]:
        """
        get index from vocabulary with word

        :param word: word of index to get
        """
        ret = []
        for i in range(len(word)):
            index = []
            for j in range(len(word[i])):
                index.append(self.__word2index[word[i][j]])
            ret.append(index)
        return ret

    def __len__(self):
        return len(self.__index2word)


class Sentence(object):
    def __init__(self, word: List[str], part: List[str], chunk: List[str], slot: List[str]):
        """
        sentence with words and slots
        """
        self.__word = deepcopy(word)
        self.__part = deepcopy(part)
        self.__chunk = deepcopy(chunk)
        self.__slot = deepcopy(slot)

    def word(self):
        """
        the words list of sentence
        """
        return deepcopy(self.__word)

    def slot(self):
        """
        the slots list of sentence
        """
        return deepcopy(self.__slot)

    def __len__(self):
        return len(self.__word)

    def __getitem__(self, index):
        return self.__word[index] + " " + self.__part[index] + " " + self.__chunk[index] + " " + self.__slot[index]


class Paragraph(object):
    def __init__(self, path: str, slot_vocabulary: Vocabulary, max_line: int = None, complete: bool = True):
        """
        sentences of paragraph

        :param slot_vocabulary: vocabulary of slot word
        :param path: path of paragraph file
        :param max_line: max lines to read
        :param complete: if data include slot
        """
        self.__sentence: List[Sentence] = []
        self.__slot_vocabulary = slot_vocabulary

        with open(path) as f:
            cnt = 0
            word: List[str] = []
            part: List[str] = []
            chunk: List[str] = []
            slot: List[str] = []

            for line in f:
                if cnt == max_line:
                    break

                item = line.strip().split()
                if len(item) == 0:
                    self.__sentence.append(Sentence(word, part, chunk, slot))
                    word = []
                    part = []
                    chunk = []
                    slot = []
                elif complete:
                    word.append(item[0])
                    part.append(item[1])
                    chunk.append(item[2])
                    slot.append(item[3])
                    self.__slot_vocabulary.add(item[3])
                else:
                    word.append(item[0])
                    part.append(item[1])
                    chunk.append(item[2])
                    slot.append("")

                cnt += 1
            self.__sentence.append(Sentence(word, part, chunk, slot))
            self.__sentence = self.__sentence[1:]

    def package(self, batch_size: int, shuffle: bool = False):
        """
        package paragraph as batch:

        :param batch_size: size of batch
        """
        words = [x.word() for x in self.__sentence]
        slots = [x.slot() for x in self.__sentence]

        return Data.DataLoader(dataset=_DataSet(words, slots),
                               batch_size=batch_size,
                               shuffle=shuffle,
                               collate_fn=_collate_fn)

    def slot_vocabulary(self):
        return self.__slot_vocabulary

    def slot(self) -> List[List[str]]:
        return [x.slot() for x in self.__sentence]

    def __len__(self):
        return len(self.__sentence)

    def __getitem__(self, index: int):
        return deepcopy(self.__sentence[index])


class _DataSet(Data.Dataset):
    def __init__(self, words: List[List[str]], slots: List[List[str]]):
        self.__words = deepcopy(words)
        self.__slots = deepcopy(slots)

    def __len__(self):
        return len(self.__words)

    def __getitem__(self, index: int):
        return self.__words[index], self.__slots[index]


def _collate_fn(batch) -> List[List[str]]:
    """
    instantiate element of batch

    :param batch: batch to be instantiated
    """
    cnt = len(batch[0])
    ret = [[] for _ in range(0, cnt)]

    for i in range(len(batch)):
        for j in range(cnt):
            ret[j].append(batch[i][j])

    return ret
