import numpy as np
from typing import List


class DatasetManager(object):
    """
    管理二维平面点的数据集
    """
    def __init__(self, min_data: float, max_data: float, x: List[float],
                 y: List[float]):
        from copy import deepcopy

        self.__x = deepcopy(x)
        self.__y = deepcopy(y)
        self.__min_data = min_data
        self.__max_data = max_data

    def x(self):
        return self.__x

    def y(self):
        return self.__y

    def min_data(self):
        return self.__min_data

    def max_data(self):
        return self.__max_data

    def load_random(self, data_number: int) -> None:
        """
        生成一定数目、给定范围内的随机点，并施加噪声

        :param data_number: 随机点的数量
        """

        import random

        self.__x = np.arange(self.__min_data, self.__max_data,
                             (self.__max_data - self.__min_data) / data_number)
        self.__y = np.sin(self.__x)
        for i in range(data_number):
            self.__x[i] += random.gauss(0, 1) / 20
            self.__y[i] += random.gauss(0, 1) / 20

    def show_data(self, name: str) -> None:
        """
        图形化显示点集中的各个点，和正弦曲线相比较
        """
        import matplotlib.pyplot as plt

        plt.title(name)

        plt.scatter(self.__x, self.__y, color='coral')
        plt.plot(self.__x, self.__y, color='coral')

        x = np.arange(self.__min_data, self.__max_data, 0.1)
        y = np.sin(x)
        plt.plot(x, y)

        plt.show()

    def loss(self) -> float:
        """
        计算该数据集关于正弦函数的均方根误差
        """

        from math import sqrt

        x = np.array(self.__x)
        y = np.array(self.__y)

        return sqrt(np.sum(pow(np.sin(x) - y, 2)) / len(x))
