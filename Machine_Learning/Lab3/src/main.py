import load
import random
import numpy as np
from data import Dataset
from process import Process
from config import args

if __name__ == "__main__":
    random.seed(args.random_seed)
    np.random.seed(args.random_seed)

    if args.file_type == "csv":
        train_x = load.load_csv(args.path + "/train.csv", 2)
        test_x = load.load_csv(args.path + "/test.csv", 2)
    if args.file_type == "txt":
        train_x = load.load_txt(args.path + "/train", 6)
        test_x = load.load_txt(args.path + "/test", 6)
    data = Dataset(train_x)

    if args.method == "k_means":
        from classifier.k_means import KMeans
        classifier = KMeans(args.kinds, args.epoch)
    if args.method == "EM":
        from classifier.EM import EM
        classifier = EM(args.kinds, args.epoch)
    module = Process(data, classifier, "kinds = " + str(args.kinds) + ", epoch = " + str(args.epoch))

    module.train()
    module.show2D()
