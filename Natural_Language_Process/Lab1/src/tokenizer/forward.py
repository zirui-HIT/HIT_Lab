from copy import deepcopy
from typing import List
from utils.vocabulary import Vocabulary
from tqdm import tqdm


class Forward(object):
    def __init__(self, vocabulary: Vocabulary):
        self.__vocabulary = deepcopy(vocabulary)

    def __call__(self, lines: List[List[str]]) -> List[List[str]]:
        ret: List[List[str]] = []
        for line in tqdm(lines):
            ret.append(self.__forward(line[0]))
        return ret

    def __forward(self, line: str) -> List[str]:
        ret: List[str] = []
        current = 0
        length = len(line)
        max_length = self.__vocabulary.max_length()

        while current < length:
            for i in reversed(range(1, min(max_length, length - current + 1))):
                phrase = self.__vocabulary.get(line[current:current + i])
                if phrase is not None:
                    ret = ret + phrase.words()
                    current = current + i
                    break
                elif i == 1:
                    ret = ret + [line[current:current + 1]]
                    current = current + 1

        return ret
