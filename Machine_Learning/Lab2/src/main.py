import load
from data import Dataset
from process import Process

from config import args

if __name__ == "__main__":
    if args.file_type == "csv":
        train_x, train_y = load.load_csv(args.path + "/train.csv", 2)
        test_x, test_y = load.load_csv(args.path + "/test.csv", 2)
    if args.file_type == "txt":
        train_x, train_y = load.load_txt(args.path + "/train", 6)
        test_x, test_y = load.load_txt(args.path + "/test", 6)

    data = Dataset(train_x, train_y)
    module = Process(data, args.method + " lamda=" + str(args.lam))

    if args.method == "gradient_without_regular":
        module.gradient_without_regular(args.learning_rate, args.eps)
    if args.method == "gradient_with_regular":
        module.gradient_with_regular(args.lam, args.learning_rate, args.eps)

    module.reload(test_x, test_y)
    print("MONK loss:" + str(module.loss()))
