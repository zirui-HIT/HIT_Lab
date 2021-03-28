import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--load_path',
                    '-lp',
                    type=str,
                    default="Lab1/data/a+b.c",
                    help="输入路径")
parser.add_argument('--dump_path',
                    '-dp',
                    type=str,
                    default='Lab1/data/a+b_analyzed.txt',
                    help="输出路径")

args = parser.parse_args()
