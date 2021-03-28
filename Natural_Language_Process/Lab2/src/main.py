from config import args
from utils.data import Paragraph
from utils.data import Vocabulary
from utils.model import BertRecognizer
from utils.processor import Processor


def set_random_seed(seed: int):
    """
    set random seed

    :param seed: random seed
    """
    import numpy
    import torch
    import random

    random.seed(seed)
    numpy.random.seed(seed)
    torch.random.manual_seed(seed)


if __name__ == '__main__':
    set_random_seed(args.random_seed)

    slot_vocabulary = Vocabulary()

    train = Paragraph(args.data_path + "/train.txt", slot_vocabulary, args.max_length)
    valid = Paragraph(args.data_path + "/valid.txt", slot_vocabulary, args.max_length)
    test = Paragraph(args.data_path + "/test.txt", slot_vocabulary, args.max_length, False)

    model = BertRecognizer(len(slot_vocabulary), args.dropout)
    processor = Processor(model)

    if args.mode == 'train':
        processor.train(train, valid)
    elif args.mode == 'test':
        processor.load(args.model_path)
        processor.predicate(test, args.save_path)
