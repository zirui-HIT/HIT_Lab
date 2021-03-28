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
        train_x, train_y = load.load_csv(args.path + "/train.csv", 3)
        test_x, test_y = load.load_csv(args.path + "/test.csv", 3)
    if args.file_type == "jpg":
        train_x, train_y = load.load_jpg(args.path)
    data = Dataset(train_x, train_y)

    module = Process(data, "PCA")
    module.PCA(800)
    module.rePCA()
    # module.show3D()
    # module.save_image(args.path)

    if args.file_type == "jpg":
        print(module.snr(data))
