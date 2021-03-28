import numpy as np
from copy import deepcopy


class Dataset(object):
    def __init__(self, x, y) -> None:
        """
        初始化数据集
        要求len(x) == len(y)

        :param x: 自变量集
        :param y: 因变量集
        """
        assert len(x) == len(y)

        self.__x = np.array(x)
        self.__y = np.array(y)

    def x(self):
        return deepcopy(self.__x)

    def y(self):
        return self.__y

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

    def kind(self):
        return max(self.__y)
