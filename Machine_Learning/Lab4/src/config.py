import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--file_type',
                    '-ft',
                    type=str,
                    default="jpg",
                    help="数据文件类型")
parser.add_argument('--path',
                    '-p',
                    type=str,
                    default="../data/face",
                    help="数据路径")
parser.add_argument('--random_seed',
                    '-rs',
                    type=int,
                    default=114514,
                    help="随机数种子")

args = parser.parse_args()
