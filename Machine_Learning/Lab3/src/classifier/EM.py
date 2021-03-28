import numpy as np
from data import Dataset
from classifier.k_means import KMeans


class EM(object):
    def __init__(self, kind: int, epoch: int):
        self.__kind = kind
        self.__epoch = epoch

    def __probability(self, x, k):
        y = (2 * np.pi)**(len(x) * 1.0 / 2) * np.linalg.det(self.__cov[k])**0.5
        x = np.exp(-0.5 * (x - self.__mean[k]) @ np.linalg.inv(self.__cov[k])
                   @ (x - self.__mean[k]).T)
        return x / y

    def __echo(self, k):
        ret = 0
        for r in self.__res:
            ret += r[k]
        return ret

    def train(self, data: Dataset):
        k_means = KMeans(self.__kind, self.__epoch)
        k_means.train(data)
        flag = k_means.predicate(data)

        self.__cov = []
        self.__mean = []
        self.__res = [[0.0] * self.__kind] * data.cnt()

        for i in range(self.__kind):
            rec = []
            for j in range(data.cnt()):
                if flag[j] == i:
                    rec.append(data.x()[j, :])
            rec = np.array(rec)

            self.__mean.append(np.mean(rec, axis=0))
            means = [self.__mean[i]] * len(rec)
            self.__cov.append((rec - means).T @ (rec - means))

        self.__mean = np.array(self.__mean)
        self.__cov = np.array(self.__cov)
        self.__res = np.array(self.__res)

        alpha = [1 / self.__kind] * self.__kind
        for e in range(self.__epoch):
            for i in range(data.cnt()):
                sigma = 0
                for j in range(self.__kind):
                    sigma += alpha[j] * self.__probability(data.x()[i], j)
                for j in range(self.__kind):
                    self.__res[i][j] = alpha[j] * self.__probability(
                        data.x()[i], j) / sigma

            for i in range(self.__kind):
                x1 = np.zeros((1, data.dim()))
                for j in range(data.cnt()):
                    x1 += self.__res[j][i] * data.x()[j, :]
                x2 = data.x() - np.tile(self.__mean[i], (data.cnt(), 1))
                x3 = np.eye(data.cnt())
                for j in range(data.cnt()):
                    x3[j][j] = self.__res[j][i]

                self.__cov[i] = x2.T @ x3 @ x2 / self.__echo(i)
                alpha[i] = self.__echo(i) / data.cnt()

    def predicate(self, data: Dataset):
        flag = []
        for i in range(data.cnt()):
            rec = self.__res[i][0]
            flag.append(0)
            for j in range(1, self.__kind):
                if self.__res[i][j] > rec:
                    rec = self.__res[i][j]
                    flag[i] = j
        return flag
