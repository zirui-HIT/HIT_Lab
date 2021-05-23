from typing import List


class Selector(object):
    def __init__(self):
        from sklearn.linear_model import LogisticRegression
        self.__model = LogisticRegression()
        self.__func = [edit_distance,
                       longest_common_sequence]

    def fit(self, document: List[List[str]], question: List[str], real_answer: List[str]):
        """训练选择器

        Args:
            document: 文档
            question: 问题
            id: 正确答案
        """
        print('selector loading train data')
        from tqdm import tqdm
        data_x = []
        data_y = []
        for i in tqdm(range(len(document))):
            for j in range(len(document[i])):
                vector = []
                for func in self.__func:
                    vector.append(func(document[i][j], question[i]))
                data_x.append(vector)

                if document[i][j] == real_answer[i]:
                    data_y.append(1)
                else:
                    data_y.append(0)

        print("training selector")
        self.__model.fit(data_x, data_y)

    def predict(self, document: List[List[str]], question: List[str], real_answer: List[str] = None) -> List[str]:
        """从文档中选择最匹配问题的一句话

        Args:
            document: 文档
            question: 问题

        Returns:
            最匹配的一句话
        """
        import numpy as np
        print("predicting")

        from tqdm import tqdm
        ans = []
        for i in tqdm(range(len(document))):
            data_x = []
            for j in range(len(document[i])):
                vector = []
                for func in self.__func:
                    vector.append(func(document[i][j], question[i]))
                data_x.append(vector)

            pred_y = self.__model.predict_proba(data_x)
            ans.append(document[i][np.argmax([pred[1] for pred in pred_y])])

        if real_answer is None:
            return ans

        cnt = 0
        for i in range(len(ans)):
            if real_answer[i] == ans[i]:
                cnt += 1
        return ans, cnt / len(document)

    def dump(self, path: str):
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self.__model, f)

    def load(self, path: str):
        import pickle
        with open(path, 'rb') as f:
            self.__model = pickle.load(f)


def edit_distance(S: str, T: str) -> int:
    """计算两个句子的编辑距离
    """
    f = [[i + j for j in range(len(T) + 1)]
         for i in range(len(S) + 1)]

    for i in range(1, len(S)+1):
        for j in range(1, len(T)+1):
            if(S[i-1] == T[j-1]):
                d = 0
            else:
                d = 1

            f[i][j] = min(f[i-1][j]+1, f[i]
                          [j-1]+1, f[i-1][j-1]+d)

    return f[len(S)][len(T)]


def longest_common_sequence(S: str, T: str) -> int:
    """计算两个句子的最长公共序列
    """
    len_str1 = len(S)
    len_str2 = len(T)
    f = [[0 for i in range(len_str2 + 1)] for j in range(len_str1 + 1)]

    for i in range(len_str1):
        for j in range(len_str2):
            if S[i] == T[j]:
                f[i + 1][j + 1] = f[i][j] + 1
            elif f[i + 1][j] > f[i][j + 1]:
                f[i + 1][j + 1] = f[i + 1][j]
            else:
                f[i + 1][j + 1] = f[i][j + 1]

    return f[-1][-1]


if __name__ == '__main__':
    DOCUM_PATH = 'Information_Retrieval/Lab2/data/raw/passages_multi_sentences.json'
    from data import DataManager
    document = DataManager.load('document', DOCUM_PATH).get('document')

    SAVE_PATH = 'Information_Retrieval/Lab2/model/LR_selector.pkl'
    selector = Selector()

    # train
    TRAIN_PATH = 'Information_Retrieval/Lab2/data/raw/QA_train.json'
    train_data = DataManager.load('train', TRAIN_PATH)
    train_question = train_data.get('question')
    train_pid = train_data.get('pid')
    train_answer = train_data.get('answer_sentence')
    train_document = [document[pid] for pid in train_pid]

    selector.fit(train_document, train_question, train_answer)
    selector.dump(SAVE_PATH)

    # valid
    selector.load(SAVE_PATH)

    VALID_PATH = 'Information_Retrieval/Lab2/data/raw/QA_valid.json'
    valid_data = DataManager.load('train', VALID_PATH)
    valid_question = valid_data.get('question')
    valid_pid = valid_data.get('pid')
    valid_answer = valid_data.get('answer_sentence')
    valid_document = [document[pid] for pid in valid_pid]

    pred_answer, score = selector.predict(
        valid_document, valid_question, valid_answer)
    print(score)
