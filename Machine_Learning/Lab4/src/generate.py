from typing import List
from copy import deepcopy


def generate_normal_distribution(save_path: str, dim: int, set_number: int,
                                 mean: List[List[float]],
                                 cov: List[List[List[float]]],
                                 points_number: List[int]) -> None:
    """
    读取一系列参数，来生成多个聚类，每个聚类内的点满足多元正态分布，将得到的结果保存在一个csv中，
    默认聚类编号为0 ~ set_number-1，自变量名为xi，i = 0 ~ dim-1

    :param save_path: 保存路径
    :param dim: 正态分布维数
    :param set_number: 聚类的数目
    :param mean: 各正态分布各维度的均值，大小为set_number * dim
    :param cov: 各正态分布的协方差矩阵，大小为set_number * dim * dim
    :param points_number: 各聚类的点的数目，大小为set_number
    """

    from numpy.random import multivariate_normal
    import pandas as pd

    result = []

    for i in range(set_number):
        normal_matrix = multivariate_normal(mean[i], cov[i], points_number[i])
        for j in range(points_number[i]):
            line = {}
            line["y"] = i
            for k in range(dim):
                line["x" + str(k)] = normal_matrix[j][k]
            result.append(deepcopy(line))

    col = []
    for i in range(dim):
        col.append("x" + str(i))
    col.append("y")

    df = pd.DataFrame(result, columns=col)
    df.to_csv(save_path, index=False)

    return None


if __name__ == "__main__":
    generate_normal_distribution("../data/test.csv", 3, 4,
                                 [[2, 2, 2], [2, -2, 2],
                                  [-2, -2, 2], [-2, 2, 2]],
                                 [[[1, 0, 0], [0, 1, 0], [0, 0, 0.1]],
                                  [[1, 0, 0], [0, 1, 0], [0, 0, 0.1]],
                                  [[1, 0, 0], [0, 1, 0], [0, 0, 0.1]],
                                  [[1, 0, 0], [0, 1, 0], [0, 0, 0.1]]],
                                 [20, 20, 20, 20])
