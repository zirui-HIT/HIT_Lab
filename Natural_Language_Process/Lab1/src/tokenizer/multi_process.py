from copy import deepcopy
from typing import List
import multiprocessing
from math import ceil


class MultiProcess(object):
    def __init__(self,
                 tokenizer,
                 process: int = ceil(multiprocessing.cpu_count() * 2 / 3)):
        self.__process = process
        self.__tokenizer = deepcopy(tokenizer)

    def __call__(self, lines: List[List[str]]) -> List[List[str]]:
        ret = multiprocessing.Manager().list()
        for i in range(len(lines)):
            ret.append([])
        process = []

        length = len(lines) // self.__process
        position = 0
        for i in range(1, self.__process):
            process.append(
                multiprocessing.Process(target=self._split,
                                        args=(
                                            lines,
                                            position,
                                            position + length,
                                            ret,
                                        )))
            position += length
        process.append(
            multiprocessing.Process(target=self._split,
                                    args=(
                                        lines,
                                        position,
                                        len(lines),
                                        ret,
                                    )))

        for p in process:
            p.start()
        for p in process:
            p.join()

        return list(ret)

    def _split(self, lines: List[List[str]], begin: int, end: int,
               ret: List[List[str]]):
        current = self.__tokenizer(lines[begin:end])
        for i in range(begin, end):
            ret[i] = current[i - begin]
