if __name__ == "__main__":
    FILE_NAME = ['QA_test.json', 'QA_train.json', 'QA_valid.json']
    FILE_PATH = 'Lab2/data/raw/'
    SAVE_PATH = 'Lab2/data/classified/'

    for f in FILE_NAME:
        TRAIN_PATH = FILE_PATH + f
        from utils.data import DataManager
        dm = DataManager.load('train_data', TRAIN_PATH)

        from utils.tokenizer import Tokenizer
        tokenizer = Tokenizer()
        dm.update(tokenizer, 'question', 'vector')

        VECTOR_PATH = 'Lab2/model/vectorizer.pkl'
        from utils.vectorizer import Vectorizer
        vectorizer = Vectorizer()
        vectorizer.load(VECTOR_PATH)
        dm.update(vectorizer, 'vector', 'vector')

        CLASS_PATH = 'Lab2/model/'
        from utils.classifier import Classifier
        classifier = Classifier()
        classifier.load(CLASS_PATH + "SVM_classifier_info.json",
                        CLASS_PATH + "SVM_classifier_model.pkl")
        dm.update(classifier, 'vector', 'field')

        DUMP_PATH = SAVE_PATH + f
        dm.delete('vector')
        dm.dump(DUMP_PATH)
