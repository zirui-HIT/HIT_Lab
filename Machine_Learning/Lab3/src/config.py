import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--file_type',
                    '-ft',
                    type=str,
                    default="csv",
                    help="数据文件类型")
parser.add_argument('--path',
                    '-p',
                    type=str,
                    default="../data/normal_distribution",
                    help="数据路径")
parser.add_argument('--method', '-m', type=str, default="EM", help="训练模型")
parser.add_argument('--kinds', '-k', type=int, default=4, help="聚类数")
parser.add_argument('--epoch', '-e', type=int, default=1, help="迭代次数")
parser.add_argument('--random_seed',
                    '-rs',
                    type=int,
                    default=114514,
                    help="随机数种子")

args = parser.parse_args()
