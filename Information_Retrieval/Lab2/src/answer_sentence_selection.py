if __name__ == "__main__":
    DOCUM_PATH = 'Lab2/data/processed_document.json'
    from utils.data import DataManager
    document_data = DataManager.load('document', DOCUM_PATH)

    VOCAB_PATH = 'Lab2/data/vocabulary.json'
    STOPS_PATH = 'Lab2/data/stopwords(new).txt'
    from utils.tokenizer import Tokenizer
    tokenizer = Tokenizer(STOPS_PATH, VOCAB_PATH, 2)
    document_data.update(tokenizer, 'context', 'vector')

    VECTO_PATH = 'Lab2/model/vectorizer.pkl'
    from utils.vectorizer import Vectorizer
    vectorizer = Vectorizer()
    vectorizer.load(VECTO_PATH)
    document_data.update(vectorizer, 'vector', 'vector')

    SELEC_PATH = 'Lab2/model/LR_selector.pkl'
    from utils.selector import Selector
    selector = Selector()
    selector.load(SELEC_PATH)

    # valid
    VALID_PATH = 'Lab2/data/raw/QA_valid.json'

    valid_data = DataManager.load('valid', VALID_PATH)
    valid_data.update(tokenizer, 'question', 'vector')
    valid_data.update(vectorizer, 'vector', 'vector')
    real_pid = valid_data.get('pid')
    question = valid_data.get('vector')

    pred_pid, score = document_data.retrieval('vector', question, real_pid)
    print(score)

    # predict
    TEST_PATH = 'Lab2/data/classified/QA_test.json'

    test_data = DataManager.load('test', TEST_PATH)
    test_data.update(tokenizer, 'question', 'vector')
    test_data.update(vectorizer, 'vector', 'vector')

    pred_pid = document_data.retrieval('vector', test_data.get('vector'))

    question = test_data.get('question')
    document = document_data.get('document')
    pred_document = [document[pid] for pid in pred_pid]
    pred_answer = selector.predict(pred_document, question)

    qid = test_data.get('qid')
    field = test_data.get('field')

    data = []
    for i in range(len(pred_answer)):
        data.append({'qid': qid[i], 'question': question[i],
                     'pid': pred_pid[i], 'answer_sentence': pred_answer[i], 'field': field[i]})

    SAVE_PATH = 'Lab2/data/test_selected.json'
    dm = DataManager('QA', data)
    dm.dump(SAVE_PATH)
