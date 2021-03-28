from typing import List


class Reducer(object):
    """降维器

    Attributes:
        __reducer: 降维器
    """

    def __init__(self, reducer=None):
        self.__reducer = reducer

    def predict(self, data: List[List[float]]) -> List[List[float]]:
        """对数据集进行降维

        Args:
            data: 降维数据，实值向量

        Returns:
            降维后的数据
        """
        print("transforming")
        return self.__reducer.transform(data).tolist()

    def fit(self, data: List[List[float]]):
        """利用数据集对降维器进行训练

        Args:
            data: 训练数据
        """
        print("fitting reducer")
        self.__reducer.fit(data)

    @staticmethod
    def load(path: str):
        """从指定路径中读取参数

        Args:
            path: 读取路径
        """
        import pickle
        with open(path, 'rb') as f:
            return Reducer(pickle.load(f))

    def dump(self, path: str):
        """保存模型参数

        Args:
            path: 保存路径
        """
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self.__reducer, f)


class PCA(Reducer):
    def __init__(self, componment=0.95):
        from sklearn.decomposition import PCA
        Reducer.__init__(self, PCA(componment))


if __name__ == '__main__':
    VECTOR_PATH = 'Lab2/model/vectorizer.pkl'
    from vectorizer import Vectorizer
    vectorizer = Vectorizer()
    vectorizer.load(VECTOR_PATH)

    from utils import FILE_NAME
    from data import DataManager
    LOAD_PATH = 'Lab2/data/tokenized/'
    SAVE_PATH = 'Lab2/data/reduced/'
    MODEL_PATH = 'Lab2/model/PCA.pkl'

    data = []
    for i in range(len(FILE_NAME)):
        dm = DataManager.load(FILE_NAME[i], LOAD_PATH + FILE_NAME[i])
        dm.update(vectorizer, 'words', 'vector')
        data = data + dm.get('vector')

    reducer = PCA(1024)
    reducer.fit(data)
    reducer.dump(MODEL_PATH)

    """
    for i in range(len(FILE_NAME)):
        dm = DataManager.load(FILE_NAME[i], LOAD_PATH + FILE_NAME[i])
        dm.update(reducer, 'vector', 'vector')
        dm.dump(SAVE_PATH + FILE_NAME[i])
    """
