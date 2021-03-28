import numpy as np
from copy import deepcopy


class Dataset(object):
    def __init__(self, x) -> None:
        """
        初始化数据集

        :param x: 点集
        """
        self.__x = deepcopy(x)

    def reload(self, X):
        """
        重新加载数据，用于训练后进行预测

        :param X: 自变量
        """
        self.__x = np.array(X)

    def x(self):
        return deepcopy(self.__x)

    def dim(self):
        return len(self.__x[0])

    def cnt(self):
        return len(self.__x)

    def min(self):
        ret = []
        for i in range(self.dim()):
            ret.append(min(self.__x.T[i]))
        return ret

    def max(self):
        ret = []
        for i in range(self.dim()):
            ret.append(max(self.__x.T[i]))
        return ret
