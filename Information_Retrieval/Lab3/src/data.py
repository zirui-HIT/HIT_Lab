from typing import Dict
from typing import List
from copy import deepcopy


class Tokenizer(object):
    """分词器

    采用哈工大LTP语言技术平台

    Attributes:
        __tokenizer: 分词器
        __vocabulary: 单词表
        __stopwords: 停用词
    """

    def __init__(self, stopwords_path: str = None):
        from ltp import LTP
        self.__tokenizer = LTP()

        self.__stopwords = None
        if not(stopwords_path is None):
            self.__stopwords = []
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                for line in f:
                    self.__stopwords.append(line.strip())

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
                current = current + w + " "
            ans.append(current.strip())
        return ans


class Vectorizer(object):
    """向量化器

    将一个已分词单词序列对应到一个实值向量
    采用tf-idf表示法

    Attributes:
        __vectorizer: 向量化器
    """

    def __init__(self, stopwords_path: str = None):
        stopwords = None
        if not(stopwords_path is None):
            stopwords = []
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                for line in f:
                    stopwords.append(line.strip())

        from sklearn.feature_extraction.text import TfidfVectorizer
        self.__vectorizer = TfidfVectorizer(stop_words=stopwords)

    def fit(self, paragraphs: List[str]):
        print('training vectorizer')
        self.__vectorizer.fit(paragraphs)

    def predict(self, paragraphs: List[str]):
        print('vectoring')
        return self.__vectorizer.transform(paragraphs).toarray()

    def dump(self, path: str):
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self.__vectorizer, f)

    def load(self, path: str):
        import pickle
        with open(path, 'rb') as f:
            self.__vectorizer = pickle.load(f)


class DataManager(object):
    """数据处理集合

    Attributes:
        __name: 数据集名称
        __len: 数据数量
        __data: 存储数据
    """

    def __init__(self, name: str, data: List[Dict]):
        self.__name = name
        self.__len = len(data)

        self.__tokenizer = Tokenizer()
        self.__vectorizer = Vectorizer()
        self.__vectorizer.load('Information_Retrieval/Lab3/model/vectorizer.pkl')

        if name != 'data':
            self.__data = deepcopy(data)
            return

        paragraphs = []
        for i in range(len(data)):
            paragraphs.append(data[i]['paragraphs'])

        paragraphs = self.__tokenizer.predict(paragraphs)
        paragraphs = self.__vectorizer.predict(paragraphs)

        for i in range(len(data)):
            data[i]['vector'] = paragraphs[i]
        self.__data = deepcopy(data)

    @staticmethod
    def load(name: str, path: str):
        """从json文件中加载数据

        Args:
            name: 数据集名称
            path: 数据路径
        """
        res = []

        import json
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                res.append(json.loads(line))
        return DataManager(name, res)

    def dump(self, path: str):
        """将数据保存到json文件

        Args:
            path: 数据路径
        """
        import json
        with open(path, 'w', encoding='utf-8') as f:
            for d in self.__data:
                json.dump(d, f, ensure_ascii=False)
                f.write('\n')

    def get(self, key: str) -> List:
        """提取键对应的属性

        Args:
            key: 属性

        Returns:
            查询属性
        """
        print('getting ' + self.__name + '--' + key)

        from tqdm import tqdm
        ret = []
        for d in tqdm(self.__data):
            ret.append(d[key])
        return ret

    def retrieval(self, question: str, K: int, authority: int) -> List[Dict]:
        """从数据库中查找和问题最匹配的文档

        Args:
            question: 原问题
            K: 最匹配文档的数量
            authority: 权限等级

        Returns:
            查找到的最匹配文档的信息
        """
        import numpy as np

        question = self.__vectorizer.predict(
            [self.__tokenizer.predict([question])[0]])[0]
        document = self.get('vector')

        current = np.matmul(document, question.T)
        for i in range(len(current)):
            if current[i] != 0:
                current[i] /= np.linalg.norm(document[i])

        pid = current.argsort()[::-1][0:len(current)]
        ret = []
        cnt = 0
        for p in pid:
            if self.__data[p]['authority'] > authority:
                continue

            ret.append(self.__data[p])
            cnt += 1

            if cnt == K:
                break
        return ret

    def delete(self, key: str):
        """刪除key對應的屬性

        Args:
            key: 刪除屬性
        """
        print('deleting ' + self.__name + '--' + key)
        from tqdm import tqdm
        for i in tqdm(range(self.__len)):
            self.__data[i].pop(key)

    def update(self, learner, key: List[str], value: str):
        """将key作为参数调用learner，将返回的结果保存到value中

        Args:
            learner: 学习器，必须声明predict
            key: 调用参数键
            value: 保存键
        """
        if isinstance(key, str):
            key = [key]

        print('updating ' + self.__name + '--' + value)
        res = self._call(learner, key)
        for i in range(self.__len):
            self.__data[i][value] = res[i]

    def _call(self, learner, key: List[str]):
        args_number = len(key)

        data = []
        for i in range(args_number):
            data.append(self.get(key[i]))

        if args_number == 1:
            return learner.predict(data[0])
        elif args_number == 2:
            return learner.predict(data[0], data[1])
        elif args_number == 3:
            return learner.predict(data[0], data[1], data[2])
