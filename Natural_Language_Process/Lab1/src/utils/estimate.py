from copy import deepcopy
from tqdm import tqdm


class Word(object):
    def __init__(self, word: str, position: int):
        self.__word = deepcopy(word)
        self.__position = position

    def word(self):
        return deepcopy(self.__word)

    def position(self):
        return self.__position

    def equal(self, o):
        """
        判断两个Word是否全相等

        :param o: 判断的另一个Word
        """
        return self.__word == o.word() and self.__position == o.position()


def esitmate(predicate_path: str, standard_path: str):
    """
    计算一个分词结果的准确率, 召回率, F1

    :param predicate: 待评估文件路径
    :param standard: 分词标准文件路径
    """
    standard = []
    with open(standard_path, 'r') as f:
        for line in f:
            p = 0
            rec = []
            words = line.split()
            for w in words:
                rec.append(Word(w, p))
                p += len(w)
            standard.append(rec)

    predicate = []
    with open(predicate_path, 'r') as f:
        for line in f:
            p = 0
            rec = []
            words = line.split()
            for w in words:
                rec.append(Word(w, p))
                p += len(w)
            predicate.append(rec)

    match = 0
    standard_cnt = 0
    predicate_cnt = 0
    print("estimating:")
    for i in tqdm(range(min(len(standard), len(predicate)))):
        standard_cnt += len(standard[i])
        predicate_cnt += len(predicate[i])
        for a in standard[i]:
            for b in predicate[i]:
                if a.equal(b):
                    match += 1

    precision = match / standard_cnt
    callback = match / predicate_cnt
    F1 = 2 * precision * callback / (precision + callback)
    return precision, callback, F1

    """
    standard_sum = 0
    standard_paragraph: List[List[str]] = []
    with open(standard, 'r') as f:
        for line in f:
            words = line.split()
            standard_paragraph.append(deepcopy(words))
            standard_sum += len(words)

    predicate_sum = 0
    match = 0
    with open(predicate, 'r') as f:
        i = 0
        for line in f:
            words = line.split()
            predicate_sum += len(words)
            for w in words:
                if w in standard_paragraph[i]:
                    match += 1
            i += 1

    precision = match / standard_sum
    callback = match / predicate_sum
    F1 = 2 * precision * callback / (precision + callback)

    return precision, callback, F1
    """
