import numpy as np
import random
import process
from config import args
from data import DatasetManager

if __name__ == '__main__':
    random.seed(args.random_seed)
    np.random.seed(args.random_seed)

    dm = DatasetManager(args.min_data, args.max_data, [], [])
    dm.load_random(args.train_range)
    dm.show_data("training set")

    x = np.arange(args.min_data, args.max_data,
                  (args.max_data - args.min_data) / args.test_range)

    if args.method == "analysis without regular":
        y = process.predicate(
            x, process.analysis_without_regular(dm, args.degree))
    elif args.method == "analysis with regular":
        y = process.predicate(
            x, process.analysis_with_regular(dm, args.degree, args.lam))
    elif args.method == "gradient descent":
        y = process.predicate(
            x,
            process.gradient_descent(dm, args.degree, args.lam,
                                     args.learning_rate, args.eps))
    elif args.method == "conjugate gradient":
        y = process.predicate(
            x, process.conjugate_descent(dm, args.degree, args.lam))

    if args.method is not None:
        dm = DatasetManager(args.min_data, args.max_data, x, y)
        dm.show_data(args.method)
