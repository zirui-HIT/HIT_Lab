from __future__ import division
import numpy as np
from typing import List
from data import DatasetManager


def predicate(x: List[float], cof: List[float]) -> List[float]:
    """
    根据给定的x和多项式，求解y

    :param x: 横坐标
    :param cof: 多项式系数
    """

    n = len(x)
    degree = len(cof)
    y: List[float] = []

    for i in range(n):
        res = 0
        pow = 1
        for j in range(degree):
            res += cof[j] * pow
            pow *= x[i]
        y.append(res)

    return np.array(y)


def analysis_without_regular(data: DatasetManager, degree: int):
    """
    根据数据集，通过解析式拟合给定阶数的多项式，不含正则化项

    :param data: 二维点集数据集
    :param degree: 多项式的阶数
    """

    n = len(data.x())
    X = np.ones((n, degree))
    for i in range(n):
        for j in range(1, degree):
            X[i][j] = X[i][j - 1] * data.x()[i]

    return np.ravel(np.mat(X.T @ X).I @ X.T @ data.y())


def analysis_with_regular(data: DatasetManager, degree: int, lam: float):
    """
    根据数据集，通过解析式拟合给定阶数的多项式，含正则化项

    :param data: 二维点集数据集
    :param degree: 多项式的阶数
    :param lam: 回归系数
    """

    degree += 1

    n = len(data.x())
    X = np.ones((n, degree))
    for i in range(n):
        for j in range(1, degree):
            X[i][j] = X[i][j - 1] * data.x()[i]

    return np.ravel(np.mat(X.T @ X + lam * np.eye(degree)).I @ X.T @ data.y())


def calc_gradient(w: List[float], x: List[float], y: List[float], lam: float):
    """
    求解给定系数的多项式在某一点的梯度，含正则化项
    """

    return (1 / len(y)) * (np.dot(x.T, np.dot(x, w) - y) + lam * w)


def gradient_descent(data: DatasetManager, degree: int, lam: float, lr: float,
                     eps: float):
    """
    根据数据集，通过梯度下降法拟合给定阶数的多项式，含正则化项

    :param data: 二维点集数据集
    :param degree: 多项式的阶数
    :param lam: 回归系数
    :param lr: 学习率
    :param eps: 梯度控制精度
    """

    degree += 1

    n = len(data.x())
    x = np.ones((n, degree))
    for i in range(n):
        for j in range(1, degree):
            x[i][j] = x[i][j - 1] * data.x()[i]
    y = data.y().reshape(n, 1)
    w = np.mat(np.zeros(degree)).T
    grad = calc_gradient(w, x, y, lam)

    while np.sum(np.absolute(grad)) > eps:
        w = w - lr * grad
        grad = calc_gradient(w, x, y, lam)

    return np.ravel(w)


def conjugate_gradient(data: DatasetManager, degree: int, lam: float):
    """
    根据数据集，通过共轭梯度法拟合给定阶数的多项式，含正则化项

    :param data: 二维点集数据集
    :param degree: 多项式的阶数
    :param lam: 回归系数
    """

    degree += 1

    n = len(data.x())
    x = np.ones((n, degree))
    for i in range(n):
        for j in range(1, degree):
            x[i][j] = x[i][j - 1] * data.x()[i]
    y = data.y().reshape(n, 1)

    Q = (1 / n) * (x.T @ x + lam * np.mat(np.eye(degree)))
    W = np.mat(np.zeros(degree)).T

    r = -calc_gradient(W, x, y, lam)
    p = r
    for i in range(1, n):
        a = float((r.T * r) / (p.T * Q * p))
        r_prev = r
        W = W + a * p
        r = r - a * Q * p
        p = r + float((r.T * r) / (r_prev.T * r_prev)) * p

    return np.ravel(W)
