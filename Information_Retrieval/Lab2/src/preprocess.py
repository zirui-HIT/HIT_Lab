if __name__ == '__main__':
    DOCUM_PATH = 'Lab2/data/raw/passages_multi_sentences.json'
    from utils.data import DataManager
    dm = DataManager.load('document', DOCUM_PATH)

    pid = dm.get('pid')
    document = dm.get('document')
    data = []
    for i in range(len(document)):
        current = ""
        for w in document[i]:
            current = current + " " + w
        data.append(
            {'pid': pid[i], 'document': document[i], 'context': current})

    SAVE_PATH = 'Lab2/data/processed_document.json'
    dm = DataManager('document', data)
    dm.dump(SAVE_PATH)
