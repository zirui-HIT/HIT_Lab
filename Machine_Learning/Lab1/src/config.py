import argparse
from math import pi

parser = argparse.ArgumentParser()

parser.add_argument('--method',
                    '-m',
                    type=str,
                    default="gradient descent",
                    help="训练模型")
parser.add_argument('--min_data',
                    '-mind',
                    type=float,
                    default=-pi,
                    help="横坐标的下界")
parser.add_argument('--max_data',
                    '-maxd',
                    type=float,
                    default=pi,
                    help="横坐标的上界")
parser.add_argument('--train_range',
                    '-trainr',
                    type=int,
                    default=20,
                    help="训练集的规模")
parser.add_argument('--test_range',
                    '-testr',
                    type=int,
                    default=20,
                    help="测试集的规模")
parser.add_argument('--degree', '-d', type=int, default=6, help="多项式阶数")
parser.add_argument('--lam', '-l', type=float, default=0.05, help="正则化系数")
parser.add_argument('--learning_rate',
                    '-lr',
                    type=float,
                    default=0.0001,
                    help="梯度下降学习率")
parser.add_argument('--eps', '-eps', type=float, default=1e-4, help="梯度下降控制精度")
parser.add_argument('--random_seed', '-rs', type=int, default=0, help="随机数种子")

args = parser.parse_args()
