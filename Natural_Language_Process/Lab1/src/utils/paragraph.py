from typing import List
from copy import deepcopy


class Paragraph(object):
    def __init__(self, lines: List[List[str]]):
        self.__lines = deepcopy(lines)
        self.__tokenized = False

    def set_tokenized(self):
        self.__tokenized = True

    def tokenized(self):
        """
        返回文章是否已经分词
        """
        return self.__tokenized

    def lines(self):
        """
        返回文章的全文
        """
        return deepcopy(self.__lines)

    def length(self):
        """
        返回文章的行数
        """
        return len(self.__lines)

    def tokenize(self, tokenizer):
        """
        根据所给的单词表、分词器对文章进行分词

        :param tokenizer: 分词器
        """
        if self.__tokenized:
            return

        print("tokenizing:")
        self.__lines = tokenizer(self.__lines)
        self.set_tokenized()

    def load(path: str, tokenized: bool, max_line: int = None):
        """
        从数据文件中读取文章
        保留空行

        :param path: 文章路径
        :param tokenized: 读取的文章是否已完成分词
        :param max_line: 最大行数
        """
        lines: List[List[str]] = []
        with open(path, 'r', encoding='utf-8') as f:
            i = 0
            for line in f:
                lines.append(line.split())
                if len(lines[i]) == 0:
                    lines[i].append('')
                i += 1
                if max_line is not None and i == max_line:
                    break

        paragraph = Paragraph(lines)
        if tokenized:
            paragraph.set_tokenized()
        return paragraph

    def save(self, path: str):
        """
        将文章保存到指定路径

        :param path: 保存路径
        """
        with open(path, 'w') as f:
            for line in self.__lines:
                for word in line:
                    f.write(word + " ")
                f.write("\n")
