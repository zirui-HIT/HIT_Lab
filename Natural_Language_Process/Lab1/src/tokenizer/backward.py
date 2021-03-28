from copy import deepcopy
from typing import List
from utils.vocabulary import Vocabulary
from tqdm import tqdm


class Backward(object):
    def __init__(self, vocabulary: Vocabulary):
        self.__vocabulary = deepcopy(vocabulary)

    def __call__(self, lines: List[List[str]]) -> List[List[str]]:
        ret: List[List[str]] = []
        for line in tqdm(lines):
            ret.append(self.__backward(line[0]))
        return ret

    def __backward(self, line: str) -> List[str]:
        ret: List[str] = []
        length = len(line)
        current = length
        max_length = self.__vocabulary.max_length()

        while current > 0:
            for i in reversed(range(1, min(max_length, current + 1))):
                phrase = self.__vocabulary.get(line[current - i:current])
                if phrase is not None:
                    ret = ret + phrase.words()[::-1]
                    current = current - i
                    break
                elif i == 1:
                    ret = ret + [line[current - 1:current]]
                    current = current - 1

        return reversed(ret)
