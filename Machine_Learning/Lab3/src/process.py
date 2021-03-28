from typing import List
from data import Dataset
from copy import deepcopy


class Process(object):
    def __init__(self, data: Dataset, classifier, name: str):
        """
        对给定点集进行K分类
        """
        self.__name = name
        self.__data = deepcopy(data)
        self.__classifier = deepcopy(classifier)

    def reload(self, X: List[List[float]]):
        """
        重新加载自变量
        用于模型训练完成后进行预测

        :param X: 重加载自变量
        """
        self.__data.reload(X)

    def train(self):
        self.__classifier.train(self.__data)

    def show2D(self) -> None:
        """
        图形化显示点集中的各个点及其所属聚类
        只显示前两维
        """
        flag = self.__classifier.predicate(self.__data)
        color = ['b', 'c', 'g', 'k', 'm', 'r', 'w', 'y']
        if self.__data.dim() < 2:
            print("illegal dim")
            return

        import matplotlib.pyplot as plt

        plt.title(self.__name)
        for i in range(self.__data.cnt()):
            plt.scatter(self.__data.x()[i][0],
                        self.__data.x()[i][1],
                        color=color[flag[i]])

        plt.show()

    def show3D(self) -> None:
        """
        图形化显示点集中的各个点及其所属聚类
        只显示前三维
        """
        flag = self.__classifier.predicate(self.__data)
        color = ['b', 'c', 'g', 'k', 'm', 'r', 'w', 'y']
        if self.__data.dim() < 3:
            print("illegal dim")
            return

        import matplotlib.pyplot as plt

        ax = plt.subplot(111, projection='3d')
        for i in range(self.__data.cnt()):
            ax.scatter(self.__data.x()[i][0], self.__data.x()[
                        i][1], self.__data.x()[i][2], color=color[flag[i]])

        plt.show()
