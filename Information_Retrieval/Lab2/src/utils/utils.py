from typing import List
from typing import Dict


FILE_NAME = ['classification_test.json', 'classification_train.json', 'classification_valid.json',
             'QA_test.json', 'QA_train.json', 'QA_valid.json']
ATTR_NAME = ['question', 'question', 'question',
             'question', 'question', 'question']


def save_json(data: List[Dict], path: str):
    """
    将数据导出为json

    :param data: 导出数据
    :param path: 导出路径
    """
    import json
    with open(path, 'w', encoding='utf-8') as f:
        for d in data:
            json.dump(d, f, ensure_ascii=False)
            f.write('\n')
