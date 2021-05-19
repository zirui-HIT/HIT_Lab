from typing import List


class Classifier(object):
    """分类器

    输入代表句子的实值向量，输出句子的分类
    其中分类可见《哈工大IR研究室问题分类体系ver2.doc》
    仅预测大类

    Attributes:
        __kind2id: 分类映射为ID
        __id2kind: ID映射为分类
        __kind_cnt: 分类的种类数
        __classifier: 分类器
    """

    def __init__(self, classifier=None):
        self.__kind2id = {}
        self.__id2kind = []
        self.__kind_cnt = 0
        self.__classifier = classifier

    def fit(self, data_x: List, data_y: List[str]):
        """利用数据集对模型进行训练

        Args:
            data_x: 训练集自变量
            data_y: 训练集因变量
        """
        print("training classifier")
        data_y = [y.split('_')[0] for y in data_y]
        for y in data_y:
            if not (y in self.__id2kind):
                self.__kind2id[y] = self.__kind_cnt
                self.__id2kind.append(y)
                self.__kind_cnt += 1
        data_y = [self.__kind2id[k] for k in data_y]

        self.__classifier.fit(data_x, data_y)

    def predict(self, data_x: List, data_y: List[str] = None):
        """用数据进行预测，僅預測大類

        Args:
            data_x: 测试集自变量
            data_y: 可选输入，测试集因变量

        Returns:
            预测结果，若输入提供了data_y，则额外返回正确率
        """
        print("predicating class")

        pred_y = self.__classifier.predict(data_x)
        pred_y = [self.__id2kind[y] for y in pred_y]

        if data_y is None:
            return pred_y

        data_y = [y.split('_')[0] for y in data_y]
        cnt = 0
        length = len(data_y)
        for i in range(length):
            if data_y[i] == pred_y[i]:
                cnt += 1
        return pred_y, cnt / length

    def dump(self, info_path: str, model_path: str):
        """将模型数据保存到指定路径

        Args:
            info_path: 信息保存路径
            model_path: 模型保存路径
        """
        import json
        info = {'kind2id': self.__kind2id, 'id2kind': self.__id2kind}
        with open(info_path, 'w') as f:
            json.dump(info, f, ensure_ascii=False)

        import pickle
        with open(model_path, 'wb') as f:
            pickle.dump(self.__classifier, f)

    def load(self, info_path: str, model_path: str):
        """从指定路径载入模型

        Args:
            info_path: 信息保存路径
            model_path: 模型保存路径
        """
        import pickle
        with open(model_path, 'rb') as f:
            self.__classifier = pickle.load(f)

        import json
        with open(info_path, 'r') as f:
            info = json.load(f)
        self.__id2kind = info['id2kind']
        self.__kind2id = info['kind2id']
        self.__kind_cnt = len(self.__kind2id)


class KNN(Classifier):
    def __init__(self, K: int):
        """KNN分类器

        Args:
            K: K近邻
        """
        from sklearn.neighbors import KNeighborsClassifier
        Classifier.__init__(self, KNeighborsClassifier(K))


class SVM(Classifier):
    def __init__(self, kind: str):
        """SVM分类器

        Args:
            kind: ovr或ovo
        """
        from sklearn.svm import SVC
        Classifier.__init__(self, SVC(decision_function_shape=kind))


if __name__ == '__main__':
    TRAIN_PATH = 'Information_Retrieval/Lab2/data/raw/classification_train.json'
    VALID_PATH = 'Information_Retrieval/Lab2/data/raw/classification_valid.json'
    from data import DataManager
    train_data = DataManager.load('train', TRAIN_PATH)
    valid_data = DataManager.load('valid', VALID_PATH)

    VOCAB_PATH = 'Information_Retrieval/Lab2/data/vocabulary.json'
    STOPS_PATH = 'Information_Retrieval/Lab2/data/stopwords(new).txt'
    from tokenizer import Tokenizer
    tokenizer = Tokenizer(STOPS_PATH, VOCAB_PATH, 2)
    train_data.update(tokenizer, 'question', 'vector')
    valid_data.update(tokenizer, 'question', 'vector')

    VECTO_PATH = 'Information_Retrieval/Lab2/model/vectorizer.pkl'
    from vectorizer import Vectorizer
    vectorizer = Vectorizer()
    vectorizer.load(VECTO_PATH)
    train_data.update(vectorizer, 'vector', 'vector')
    valid_data.update(vectorizer, 'vector', 'vector')

    # train
    classifier = SVM('ovr')
    train_x = train_data.get('vector')
    train_y = train_data.get('field')
    classifier.fit(train_x, train_y)

    CLASS_PATH = 'Information_Retrieval/Lab2/model/'
    classifier.dump(CLASS_PATH + 'SVM_classifier_info.json',
                    CLASS_PATH + 'SVM_classifier_model.pkl')

    # valid
    valid_x = valid_data.get('vector')
    valid_y = valid_data.get('field')
    pred_y, score = classifier.predict(valid_x, valid_y)
    print(score)
