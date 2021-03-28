from typing import List


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


if __name__ == '__main__':
    from utils import FILE_NAME, ATTR_NAME
    DATA_PATH = 'Lab2/data/raw/'

    STOPWORD_PATH = 'Lab2/data/stopwords(new).txt'
    VOCABULARY_PATH = 'Lab2/data/vocabulary.json'
    from tokenizer import Tokenizer
    tokenizer = Tokenizer(STOPWORD_PATH, VOCABULARY_PATH, 2)

    from data import DataManager
    data = []
    for i in range(len(FILE_NAME)):
        dm = DataManager.load(FILE_NAME[i], DATA_PATH + FILE_NAME[i])
        dm.update(tokenizer, ATTR_NAME[i], ATTR_NAME[i])
        data = data + dm.get(ATTR_NAME[i])

    # 特殊处理document
    dm = DataManager.load('document', DATA_PATH +
                          'passages_multi_sentences.json')
    document = dm.get('document')
    rec = []
    for d in document:
        current = ""
        for w in d:
            current = current + w
        rec.append(current)
    rec = tokenizer.predict(rec)
    data = data + rec

    vectorizer = Vectorizer(STOPWORD_PATH)
    vectorizer.fit(data)

    SAVE_PATH = 'Lab2/model/vectorizer.pkl'
    vectorizer.dump(SAVE_PATH)
