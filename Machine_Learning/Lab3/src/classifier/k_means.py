import numpy as np
from data import Dataset


class KMeans(object):
    def __init__(self, kind: int, epoch: int):
        self.__kind = kind
        self.__epoch = epoch
        self.__train = False

    def __calc_distance(self, x1, y1, x2, y2):
        """
        计算两点间的距离
        """
        from math import sqrt
        dx = x1 - x2
        dy = y1 - y2
        return sqrt(dx * dx + dy * dy)

    def train(self, data: Dataset):
        """
        利用k-means算法求解聚类问题

        :param data: 训练集
        """
        self.__train = True

        core = np.random.rand(data.dim(), self.__kind)
        for i in range(data.dim()):
            core[i] = data.min()[i] + core[i] * (data.max()[i] - data.min()[i])
        core = core.T
        self.__core = Dataset(core)

        for e in range(self.__epoch):
            flag = self.predicate(data)
            agg = np.array([[0.0] * data.dim()] * self.__kind)
            cnt = np.array([0] * self.__kind)

            for i in range(data.cnt()):
                cnt[flag[i]] += 1
                agg[flag[i]] += data.x()[i]

            core = []
            for i in range(self.__kind):
                core.append(agg[i] / cnt[i])
            self.__core.reload(np.array(core))

    def predicate(self, data: Dataset):
        """
        按照最近距离将每个点分配到最近的聚类
        """
        if self.__train is False:
            raise Exception("Classifier is not trained")

        ret = [0] * data.cnt()
        for i in range(data.cnt()):
            distance = float("INF")
            flag = -1
            for j in range(self.__kind):
                d = self.__calc_distance(data.x()[i][0],
                                         data.x()[i][1],
                                         self.__core.x()[j][0],
                                         self.__core.x()[j][1])
                if d < distance:
                    distance = d
                    flag = j
            ret[i] = flag
        return ret
