from typing import List
from typing import Dict


class Vocabulary(object):
    """单词表

    Attributes:
        __word_cnt: 单词总数
        __vocabulary: 单词数据，记录每个单词出现的次数和出现的文档总数
        __word2id: 将单词对应到id
    """

    def __init__(self):
        self.__word_cnt = 0
        self.__vocabulary: List[Dict] = []
        self.__word2id = {}

    def append(self, word: List[str]):
        """向单词表中添加单词

        Args:
            word: 待添加单词序列
        """
        rec = []
        for w in word:
            if w in self.__word2id:
                self.__vocabulary[self.__word2id[w]]['appear_frequency'] += 1

                if not (w in rec):
                    self.__vocabulary[
                        self.__word2id[w]]['document_frequency'] += 1
                    rec.append(w)
            else:
                self.__vocabulary.append({
                    'word': w,
                    'appear_frequency': 1,
                    'document_frequency': 1
                })
                self.__word2id[w] = self.__word_cnt
                self.__word_cnt += 1

    def dump(self, path: str):
        """将单词表导出为json

        Args:
            path: 导出路径
        """
        from utils import save_json
        save_json(self.__vocabulary, path)

    def load(self, path: str):
        """从json读取单词表

        Args:
            path: 导入路径
        """
        self.__word_cnt = 0
        self.__vocabulary = []
        self.__word2id = {}

        import json
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                current = json.loads(line)
                self.__vocabulary.append(current)
                self.__word2id[self.__vocabulary[self.__word_cnt]
                               ['word']] = self.__word_cnt
                self.__word_cnt += 1

    def get_word(self, id: int) -> Dict:
        """通过id获取相应的单词

        Args:
            id: 待获取id

        Returns:
            相应单词
        """
        return self.__vocabulary[id]

    def get_id(self, word: str) -> int:
        """通过单词获取id

        Args:
            word: 待获取单词

        Returns:
            相应单词
        """
        if not(word in self.__word2id):
            return None
        return self.__word2id[word]


class Tokenizer(object):
    """分词器

    采用哈工大LTP语言技术平台

    Attributes:
        __tokenizer: 分词器
        __vocabulary: 单词表
        __stopwords: 停用词
    """

    def __init__(self, stopwords_path: str = None, vocabulary_path: str = None, limit: int = 0):
        from ltp import LTP
        self.__tokenizer = LTP()

        self.__vocabulary = None
        if not(vocabulary_path is None):
            self.__vocabulary = Vocabulary()
            self.__vocabulary.load(vocabulary_path)

        self.__stopwords = None
        if not(stopwords_path is None):
            self.__stopwords = []
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                for line in f:
                    self.__stopwords.append(line.strip())

        self.__limit = limit

    def predict(self, paragraph: List[str]) -> List[str]:
        """对给定的文段进行分词处理，用空格区分

        Args:
            paragraph: 待分词文段
            limit: 删除频率小于limit的低频词

        Returns:
            分词结果，用空格分隔
        """
        print('tokenizing')
        i = 0
        ret = []
        while i <= len(paragraph):
            r = min(i+256, len(paragraph))
            current, _ = self.__tokenizer.seg(paragraph[i: r])

            ret = ret + current
            i += 256

        ans = []
        for p in ret:
            current = ""
            for w in p:
                if not(self.__stopwords is None) and w in self.__stopwords:
                    continue
                if not(self.__vocabulary is None) and self.__limit > 0:
                    i = self.__vocabulary.get_id(w)
                    if i is None:
                        continue
                    c = self.__vocabulary.get_word(i)['appear_frequency']
                    if c < self.__limit:
                        continue
                current = current + w + " "
            ans.append(current.strip())
        return ans
