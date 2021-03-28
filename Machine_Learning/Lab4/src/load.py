import numpy as np


def load_csv(path: str, dim: int):
    """
    从csv文件中读取训练的数据
    要求csv中自变量列为x_i，因变量列为y

    :param path: csv文件路径
    :param dim: 自变量维数
    """
    import pandas as pd

    data = pd.read_csv(path)

    x = []
    for i in range(dim):
        x.append(data['x' + str(i)])
    x = np.array(x).T
    y = np.array(data['y'])

    return x, y


def load_jpg(path: str):
    import os
    from PIL import Image

    cnt = 0
    x = []
    dirs = os.listdir(path)
    for file_name in dirs:
        if file_name.split('.')[1] != 'py':
            img = np.asarray(Image.open(path + "/" + file_name))
            img = img.tolist()
            tmp = []
            for line in img:
                tmp = tmp + line
            x.append(tmp)
            cnt += 1

    return np.array(x), np.array([0] * cnt)
