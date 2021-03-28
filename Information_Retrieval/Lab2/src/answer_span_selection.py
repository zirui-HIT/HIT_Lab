from typing import List


class Selector(object):
    def __init__(self):
        pass

    def predict(self, sentences: List[str], annotations: List[List[str]], field: List[str]):
        sentences = [s.split() for s in sentences]
        ans = []

        print("selecting answer")
        from tqdm import tqdm
        for i in tqdm(range(len(sentences))):
            current = ""
            flag = False
            for j in range(len(sentences[i])):
                if annotations[i][j] != 'O':
                    a = annotations[i][j].split('-')
                    if a[1] != field[i]:
                        continue

                    if a[0] == 'B':
                        flag = True
                    current = current + sentences[i][j]
                elif flag:
                    break

            if len(current) > 0:
                ans.append(current)
            else:
                # TODO
                ans.append("")

        return ans


if __name__ == '__main__':
    DATA_PATH = 'Lab2/data/test_selected.json'
    from utils.data import DataManager
    dm = DataManager.load('data', DATA_PATH)

    from utils.tokenizer import Tokenizer
    tokenizer = Tokenizer()
    dm.update(tokenizer, 'answer_sentence', 'sentence_vector')

    RECO_PATH = 'Lab2/model/CRF_recognizer.pkl'
    from utils.recognizer import Recognizer
    recognizer = Recognizer()
    recognizer.load(RECO_PATH)
    dm.update(recognizer, 'sentence_vector', 'annotation')

    selector = Selector()
    dm.update(selector, ['sentence_vector', 'annotation', 'field'], 'answer')

    SAVE_PATH = 'Lab2/data/test_answer.json'
    dm.delete('answer_sentence')
    dm.delete('sentence_vector')
    dm.delete('annotation')
    dm.delete('field')
    dm.dump(SAVE_PATH)
