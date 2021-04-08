import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--load_path',
                    '-lp',
                    type=str,
                    default="Compile_System/Lab1/data/input.c",
                    help="输入路径")
parser.add_argument('--dump_path',
                    '-dp',
                    type=str,
                    default='Compile_System/Lab1/data/result.txt',
                    help="输出路径")
parser.add_argument('--log_path',
                    '-log',
                    type=str,
                    default='Compile_System/Lab1/data/error.log',
                    help="错误日志")

args = parser.parse_args()
