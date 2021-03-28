from copy import deepcopy
from typing import List
from utils.phrase import Phrase


class Trie(object):
    def __init__(self, initial_length=1024):
        self.__base = [0] * initial_length
        self.__check = [0] * initial_length
        self.__phrase = [None] * initial_length
        self.__length = initial_length

        self.__char_list = set()
        self.__position = 1

        self.__base[0] = 1

    def add(self, phrase: Phrase) -> None:
        """
        向Trie中添加一个phrase

        :param phrase: 待添加的词组
        """
        last = 0
        current = 0
        s = phrase.phrase(sep='')

        for w in s:
            code = self.__encode(w)
            current = abs(self.__base[last]) + code

            while current >= self.__length:
                self.__extend()

            if self.__base[current] == 0:
                # 当前位置为空
                self.__base[current] = self.__position
                self.__position += 1
            elif self.__check[current] != last:
                # 当前位置已被占用
                childs = self.__get_childs(last)
                avail_base = self.__get_avail(childs + [code])
                last_base = abs(self.__base[last])

                for x in childs:
                    self.__base[avail_base + x] = self.__base[last_base + x]
                    self.__check[avail_base + x] = self.__check[last_base + x]
                    self.__phrase[avail_base + x] = self.__phrase[last_base +
                                                                  x]

                    if self.__base[last_base + x] != 0:
                        grandsons = self.__get_childs(last_base + x)
                        for y in grandsons:
                            self.__check[self.__base[last_base + x] +
                                         y] = avail_base + x

                    self.__base[last_base + x] = 0
                    self.__check[last_base + x] = 0
                    self.__phrase[last_base + x] = None
                if self.__base[last] < 0:
                    self.__base[last] = -avail_base
                else:
                    self.__base[last] = avail_base

                current = avail_base + code
                self.__base[current] = self.__position
                self.__position += 1

            self.__check[current] = last
            last = current

        self.__base[current] = -abs(self.__base[current])
        self.__phrase[current] = deepcopy(phrase)

    def get(self, phrase: str) -> Phrase:
        """
        在Trie中检索某个词组是否存在
        若不存在，则返回None；否则，返回相应的Phrase

        :param phrase: 待检索的Phrase
        """
        last = 0
        current = 0

        for w in phrase:
            code = self.__encode(w)
            current = abs(self.__base[last]) + code

            if current >= self.__length:
                return None

            if self.__check[current] != last:
                return None
            last = current

        if self.__base[current] < 0:
            return deepcopy(self.__phrase[current])
        return None

    def __extend(self):
        """
        扩张base和check的大小
        每次变为原来的两倍
        """
        self.__base += [0] * self.__length
        self.__check += [0] * self.__length
        self.__phrase += [None] * self.__length
        self.__length <<= 1

    def __get_childs(self, position: int) -> List[int]:
        """
        返回所有position孩子的code

        :param position: 待查询节点
        """
        ret: List[int] = []
        base = abs(self.__base[position])
        for x in self.__char_list:
            if base + x < self.__length and self.__check[base + x] == position:
                ret.append(x)
        return ret

    def __get_avail(self, offset: List[int]) -> int:
        """
        探测所有偏置均为0的起始位置

        :param offest: 偏置
        """
        p = 1
        while True:
            flag = True
            for x in offset:
                while p + x >= self.__length:
                    self.__extend()
                if self.__base[p + x] != 0:
                    flag = False
                    break

            if flag:
                return p
            p += 1

    def __encode(self, character) -> int:
        """
        将一个字符编码为数字
        保证无冲突

        :param character: 待编码字符
        """
        byte = character.encode('GBK')
        if len(byte) == 1:
            code = byte[0]
        else:
            code = (byte[0] - 0x81) * 190 + (byte[1] - 0x40) - (byte[1] // 128)

        self.__char_list.add(code)
        return code
