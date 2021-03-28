class Retrievaler(object):
    def __init__(self):
        pass

    def predict(self, data, question):
        """
        检索问题对应数据

        :param data: 检索数据
        :param question: 检索问题
        """
        import numpy as np
        data = np.array(data)
        question = np.array(question)

        res = data @ question.T
        return np.argmax(res)


if __name__ == '__main__':
    DATA_PATH = 'Lab2/data/tokenized/passages_multi_sentences.json'
    QUES_PATH = 'Lab2/data/tokenized/QA_train.json'
    VECT_PATH = 'Lab2/model/vectorizer.pkl'
    REDU_PATH = 'Lab2/model/PCA.pkl'

    from data import DataManager
    data = DataManager.load('document', DATA_PATH)
    ques = DataManager.load('question', QUES_PATH)

    from vectorizer import Vectorizer
    vectorizer = Vectorizer()
    vectorizer.load(VECT_PATH)
    data.update(vectorizer, 'words', 'vector')
    ques.update(vectorizer, 'words', 'vector')

    from reducer import PCA
    reducer = PCA.load(REDU_PATH)
    data.update(reducer, 'vector', 'vector')
    ques.update(reducer, 'vector', 'vector')

    retrievaler = Retrievaler()
    ques_data = ques.get('vector')
    pred_ans = data.retrieval(retrievaler, ques_data)

    real_ans = ques.get('pid')
    cnt = 0
    for i in range(len(real_ans)):
        if real_ans[i] == pred_ans[i]['pid']:
            cnt += 1
    print(cnt / len(real_ans))
