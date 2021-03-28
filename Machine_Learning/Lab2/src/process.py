import numpy as np
from typing import List
from data import Dataset
from copy import deepcopy


class Process(object):
    def __init__(self, data: Dataset, name: str):
        """
        逻辑回归
        仅处理二分类的情况
        """
        self.__name = name
        self.__data = deepcopy(data)
        self.__coef = np.zeros([self.__data.dim(), 1])

    def reload(self, X: List[List[float]], Y: List[int]):
        """
        重新加载自变量，并将y清零
        用于模型训练完成后进行预测
        """
        self.__data.reload(X, Y)

    def gradient(self, lam: float):
        x = np.mat(self.__data.x())
        y = np.mat(self.__data.y())

        return x.T @ (y.T - 1 /
                      (1 + np.exp(x @ self.__coef))) + lam * self.__coef

    def gradient_without_regular(self, lr: float, eps: float) -> None:
        """
        牛顿下降进行拟合，不含正则项

        :param lr: 学习率
        :param eps: 控制精度
        """
        gradient = self.gradient(0)

        while np.sum(np.absolute(gradient)) > eps:
            self.__coef = self.__coef - lr * gradient
            gradient = self.gradient(0)

    def gradient_with_regular(self, lam: float, lr: float, eps: float) -> None:
        """
        牛顿下降进行拟合，含正则项

        :param lam: 正则化系数
        :param lr: 学习率
        :param eps: 控制精度
        """
        gradient = self.gradient(lam)

        while np.sum(np.absolute(gradient)) > eps:
            self.__coef = self.__coef - lr * gradient
            gradient = self.gradient(lam)

    def predict(self) -> List[int]:
        """
        对所给数据进行预测
        """
        from math import exp

        Y = []
        for x in self.__data.x():
            y = 1 / (1 + exp(-self.__coef.T @ x))
            if y > 0.5:
                Y.append(1)
            else:
                Y.append(0)

        return np.array(Y)

    def loss(self) -> float:
        """
        计算损失函数
        """
        from math import exp
        from math import log

        X = self.__data.x()
        Y = self.__data.y()
        pred = self.predict()
        loss = 0

        for i in range(self.__data.cnt()):
            if Y[i] != pred[i]:
                loss += log(1 + exp(-self.__coef.T @ X[i]))

        return loss / self.__data.cnt()

    def show(self, x_dim: int, y_dim: int) -> None:
        """
        图形化显示点集中的各个点
        受matplotlib的限制，只能显示两维

        :param x_dim: 横坐标维度
        :param y_dim: 纵坐标维度
        """
        color = ['b', 'c', 'g', 'k', 'm', 'r', 'w', 'y']

        import matplotlib.pyplot as plt

        plt.title(self.__name)
        for i in range(self.__data.cnt()):
            plt.scatter([self.__data.x()[i][x_dim]],
                        [self.__data.x()[i][y_dim]],
                        color=color[self.__data.y()[i] + 1])

        line_x = np.arange(self.__data.min()[x_dim],
                           self.__data.max()[x_dim], 0.1)
        line_y = -(self.__coef[x_dim] * line_x) / self.__coef[y_dim]
        line_y = line_y.T

        plt.plot(line_x, line_y, color=color[0])

        plt.show()
