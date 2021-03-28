from typing import List


class Annotator(object):
    def __init__(self):
        pass

    def predict(self, sentences: List[str], answer: List[str], field: List[str]) -> List[str]:
        """对句子进行标注

        对句子中对应答案的部分，标注为相应的类别
        采用BIO标注法

        Args:
            sentences: 句子，空格做分词
            answer: 答案，空格做分词
            field: 问题所属类别

        Returns:
            标注后的BIO序列，用空格分隔
        """
        ret = []
        print("annotating")
        from tqdm import tqdm
        for i in tqdm(range(len(sentences))):
            current_sentence = sentences[i].split()
            current_answer = answer[i].split()
            current_field = field[i]
            current_result = ""

            flag = False
            for j in range(len(current_sentence)):
                if not(current_sentence[j] in current_answer):
                    if flag:
                        flag = False
                    current_result = current_result + "O" + " "
                elif flag:
                    current_result = current_result + "I-" + current_field + " "
                else:
                    current_result = current_result + 'B-' + current_field + " "
                    flag = True

            ret.append(current_result)

        return ret


class Recognizer(object):
    def __init__(self):
        from sklearn_crfsuite import CRF
        self.__model = CRF(
            algorithm='lbfgs',
            c1=0.1,
            c2=0.1,
            max_iterations=100,
            all_possible_transitions=True
        )

    def _word2feature(self, words: List[str], position: int) -> List[str]:
        """根据句中单词得到其特征

        Args:
            word: 提取特征单词列表
            position: 单词在句中的位置

        Returns：
            记录了各项特征的列表
        """
        word = words[position]
        features = {
            'bias': 1.0,
            'word.lower()': word.lower(),
            'word[-3:]': word[-3:],
            'word[-2:]': word[-2:],
            'word.isupper()': word.isupper(),
            'word.istitle()': word.istitle(),
            'word.isdigit()': word.isdigit()
        }

        if position > 0:
            word1 = words[position-1]
            features.update({
                '-1:word.lower()': word1.lower(),
                '-1:word.istitle()': word1.istitle(),
                '-1:word.isupper()': word1.isupper()
            })
        else:
            features['BOS'] = True

        if position < len(words)-1:
            word1 = words[position+1]
            features.update({
                '+1:word.lower()': word1.lower(),
                '+1:word.istitle()': word1.istitle(),
                '+1:word.isupper()': word1.isupper()
            })
        else:
            features['EOS'] = True

        return features

    def fit(self, words: List[str], annotations: List[str]):
        """利用CRF进行命名实体识别

        Args:
            words: 句子，已用空格做好分词
            annotations: 标注序列，每个用空格分隔
        """
        print("training recognizer")
        words = [w.split() for w in words]

        data_x = [[self._word2feature(ls, i)
                   for i in range(len(ls))] for ls in words]
        data_y = [a.split() for a in annotations]

        self.__model.fit(data_x, data_y)

    def predict(self, words: List[str], annotations: List[str] = None) -> List[List[str]]:
        """利用CRF进行命名实体识别

        Args:
            words: 句子，已用空格做好分词

        Returns:
            标注序列
        """
        print("recognizing annotations")

        words = [w.split() for w in words]
        data_x = [[self._word2feature(ls, i)
                   for i in range(len(ls))] for ls in words]

        pred_y = self.__model.predict(data_x)

        if annotations is None:
            return pred_y

        data_y = [a.split() for a in annotations]
        cnt = 0
        for i in range(len(data_y)):
            flag = False
            for j in range(len(data_y[i])):
                if data_y[i][j] != pred_y[i][j]:
                    flag = True
                    break
            if not flag:
                cnt += 1

        return pred_y, cnt / len(data_y)

    def dump(self, path: str):
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self.__model, f)

    def load(self, path: str):
        import pickle
        with open(path, 'rb') as f:
            self.__model = pickle.load(f)


if __name__ == '__main__':
    TRAIN_PATH = 'Lab2/data/raw/QA_train.json'
    VALID_PATH = 'Lab2/data/raw/QA_valid.json'
    from data import DataManager
    train_data = DataManager.load('train_data', TRAIN_PATH)
    valid_data = DataManager.load('valid_data', VALID_PATH)

    from tokenizer import Tokenizer
    tokenizer = Tokenizer()
    train_data.update(tokenizer, 'question', 'question_words')
    train_data.update(tokenizer, 'answer', 'answer_words')
    train_data.update(tokenizer, 'answer_sentence', 'sentence_words')
    valid_data.update(tokenizer, 'question', 'question_words')
    valid_data.update(tokenizer, 'answer', 'answer_words')
    valid_data.update(tokenizer, 'answer_sentence', 'sentence_words')

    VECTOR_PATH = 'Lab2/model/vectorizer.pkl'
    from vectorizer import Vectorizer
    vectorizer = Vectorizer()
    vectorizer.load(VECTOR_PATH)
    train_data.update(vectorizer, 'question_words', 'vector')
    valid_data.update(vectorizer, 'question_words', 'vector')

    """
    REDU_PATH = 'Lab2/model/PCA.pkl'
    from reducer import PCA
    reducer = PCA.load(REDU_PATH)
    train_data.update(reducer, 'vector', 'vector')
    valid_data.update(reducer, 'vector', 'vector')
    """

    CLASS_PATH = 'Lab2/model/'
    from classifier import Classifier
    classifier = Classifier()
    classifier.load(CLASS_PATH + 'SVM_classifier_info.json',
                    CLASS_PATH + 'SVM_classifier_model.pkl')
    train_data.update(classifier, 'vector', 'field')
    valid_data.update(classifier, 'vector', 'field')

    annotator = Annotator()
    train_data.update(annotator, ['sentence_words',
                                  'answer_words', 'field'], 'annotation')
    valid_data.update(annotator, ['sentence_words',
                                  'answer_words', 'field'], 'annotation')

    # train
    train_words = train_data.get('sentence_words')
    train_annotations = train_data.get('annotation')
    recognizer = Recognizer()
    recognizer.fit(train_words, train_annotations)

    SAVE_PATH = 'Lab2/model/CRF_recognizer.pkl'
    recognizer.dump(SAVE_PATH)

    # test
    valid_words = valid_data.get('sentence_words')
    valid_annotation = valid_data.get('annotation')
    pred_y, acc = recognizer.predict(valid_words, valid_annotation)
