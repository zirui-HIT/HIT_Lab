import numpy as np
import pandas as pd


def load_csv(path: str, dim: int):
    """
    从csv文件中读取训练的数据
    要求csv中自变量列为x_i，因变量列为y

    :param path: csv文件路径
    :param dim: 自变量维数
    """
    data = pd.read_csv(path)

    x = []
    for i in range(dim):
        x.append(data['x' + str(i)])
    x = np.array(x).T
    y = np.array(data['y'])

    return x, y


def load_txt(path: str, dim: int):
    """
    从txt文件中读取训练的数据
    要求txt中第一列为因变量，后面依次为自变量

    :param path: txt文件路径
    :param dim: 自变量维数
    """
    x = []
    y = []
    with open(path, 'r') as f:
        for line in f:
            words = line.split()
            y.append(int(words[0]))

            t = []
            for i in range(1, dim + 1):
                t.append(float(words[i]))
            x.append(t)

    x = np.array(x)
    y = np.array(y)

    return x, y
