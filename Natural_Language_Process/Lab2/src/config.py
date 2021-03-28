import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--random_seed',
                    '-rs',
                    type=int,
                    default=0,
                    help="random seed")
parser.add_argument('--mode', '-m', type=str, default='test',
                    help="which to train or test model")

parser.add_argument('--data_path',
                    '-dp',
                    type=str,
                    default='../data',
                    help="path of data")
parser.add_argument('--model_path',
                    '-mp',
                    type=str,
                    default='../model/model.pkl',
                    help="path to save model")
parser.add_argument('--save_path', '-sp', type=str,
                    default='../out.txt', help="ooutput path")
parser.add_argument('--max_length',
                    '-ml',
                    type=int,
                    default=None,
                    help="max length to be processed")

parser.add_argument('--epoch', '-e', type=int, default=20, help="epoch")
parser.add_argument('--batch_size',
                    '-bs',
                    type=int,
                    default=4,
                    help="batch size")
parser.add_argument('--learning_rate',
                    '-lr',
                    type=float,
                    default=1e-5,
                    help="learing rate")
parser.add_argument('--dropout', '-d', type=float, default=0.3, help="dropout")

args = parser.parse_args()
