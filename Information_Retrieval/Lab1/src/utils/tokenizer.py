from ltp import LTP
from typing import List


class Tokenizer(object):
    def __init__(self, stopwords_path: str):
        self.__tokenizer = LTP()

        self.__stopwords = []
        with open(stopwords_path, 'r', encoding='utf-8') as f:
            for line in f:
                self.__stopwords.append(line.strip())

    def __call__(self, paragraphs: str) -> List[str]:
        """对给定的文段进行分词处理

        Args:
            paragraphs: 待分词文段

        Returns:
            分词文段
        """
        if isinstance(paragraphs, str):
            paragraphs = paragraphs.strip()
            if len(paragraphs) == 0:
                return []
            return self.__tokenize_list([paragraphs])[0]
        else:
            return self.__tokenize_list(paragraphs)

    def __tokenize_list(self, paragraph: List[str]):
        ret, _ = self.__tokenizer.seg(paragraph)
        ans = []
        for p in ret:
            current = []
            for w in p:
                if not(w in self.__stopwords):
                    current.append(w)
            ans.append(current)
        return ans
