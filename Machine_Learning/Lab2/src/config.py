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
                    default="../data/unrelated_normal_distribution",
                    help="数据路径")
parser.add_argument('--method',
                    '-m',
                    type=str,
                    default="gradient_with_regular",
                    help="训练模型")
parser.add_argument('--lam', '-l', type=float, default=0.05, help="正则化系数")
parser.add_argument('--learning_rate',
                    '-lr',
                    type=float,
                    default=0.0001,
                    help="梯度下降学习率")
parser.add_argument('--eps', '-eps', type=float, default=1e-4, help="梯度下降控制精度")
parser.add_argument('--random_seed', '-rs', type=int, default=0, help="随机数种子")

args = parser.parse_args()
