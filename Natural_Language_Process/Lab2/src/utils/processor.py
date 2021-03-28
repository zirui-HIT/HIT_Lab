from copy import deepcopy
from tqdm import tqdm
from typing import List

import numpy as np

import torch
from transformers import AdamW

from config import args
from utils.data import Paragraph
from utils.tokenizer import Tokenizer
from utils.metric import ExternalMetrics


class Processor(object):
    def __init__(self, model):
        """
        model process that can be trained and predicate

        :param model: model to use
        """
        self.__model = deepcopy(model)
        self.__tokenizer = Tokenizer()
        self.__optimizer = AdamW(
            self.__model.parameters(), lr=args.learning_rate)
        self.__loss_function = torch.nn.NLLLoss()

        if torch.cuda.is_available():
            self.__model = self.__model.cuda()
            self.__loss_function = self.__loss_function.cuda()

    def train(self, dataset: Paragraph, valid_dataset: Paragraph = None):
        """
        train model with dataset

        :param dataset: dataset used to train model
        :param valid_dataset: dataset used to valid
        """
        self.__model.train()
        if valid_dataset is not None:
            _, best_f1 = self.estimate(valid_dataset)

        param = []

        for epoch in range(args.epoch):
            print("epoch" + str(epoch) + ":")
            batch = dataset.package(args.batch_size, True)

            for current_word, current_slot in tqdm(batch, ncols=len(batch)):
                word, span, mask = self.__wrap_word(current_word)

                list_slot = list(self.__expand_slot(current_slot))
                index_slot = dataset.slot_vocabulary().word2index([
                    list_slot])[0]
                slot = torch.tensor(index_slot, dtype=torch.long)

                if torch.cuda.is_available():
                    word = word.cuda()
                    mask = mask.cuda()
                    slot = slot.cuda()

                predicate = self.__model(word, mask, span)
                loss = self.__loss_function(predicate, slot)

                self.__optimizer.zero_grad()
                loss.backward()
                self.__optimizer.step()

            if valid_dataset is not None:
                _, f1 = self.estimate(valid_dataset)
                if f1 > best_f1:
                    best_f1 = f1
                    torch.save(self.__model, args.model_path)
                print(best_f1)

            param.append(list(self.__model.parameters()))

    def predicate(self, dataset: Paragraph, save_path: str = None) -> List[List[str]]:
        """
        predicate slot of sentences

        :param dataset: dataset to be predicated
        :param save_path: save result if not None
        """
        self.__model.eval()
        batch = dataset.package(args.batch_size, False)
        index = []
        real_slot = []

        for current_word, current_slot in tqdm(batch, ncols=len(batch)):
            word, span, mask = self.__wrap_word(current_word)
            real_slot.extend(current_slot)

            if torch.cuda.is_available():
                word = word.cuda()
                mask = mask.cuda()

            predicate = self.__model(word, mask, span)
            _, slot = predicate.topk(1, dim=1)
            index.extend(slot)

        predicate_slot = []
        last = 0
        for i in range(len(real_slot)):
            predicate_slot.append(
                [int(x) for x in index[last: last + len(real_slot[i])]])
            last += len(real_slot[i])
        predicate_slot = dataset.slot_vocabulary().index2word(predicate_slot)

        if save_path is not None:
            with open(save_path, "w") as f:
                f.write("-DOCSTART- -X- -X- O" + "\n" + "\n")
                for i in range(len(dataset)):
                    sentence = dataset[i]
                    for j in range(len(predicate_slot[i])):
                        f.write(sentence[j] + predicate_slot[i][j] + "\n")
                    f.write("\n")

        return predicate_slot, real_slot

    def estimate(self, dataset: Paragraph):
        """
        calc accuracy and F1

        :param predicate:
        :param real:
        """
        predicate, real = self.predicate(dataset)

        acc = ExternalMetrics.accuracy(predicate, real)
        f1 = ExternalMetrics.f1_score(predicate, real)

        return acc, f1

    def load(self, model_path: str):
        """
        load trained model from path

        :param model_path: path of model
        """
        self.__model = torch.load(model_path)

    def __wrap_word(self, batch: List[List[str]]):
        """
        change word batch to piece batch,
        and padding the result
        """
        piece, span = self.__tokenizer(batch)
        piece = self.__add_padding_cls_sep(piece)

        index = [self.__tokenizer.piece2index(x) for x in piece]
        index = torch.tensor(index, dtype=torch.long)

        mask = torch.tensor(np.where(index != 0, 1, 0))

        return index, span, torch.as_tensor(mask)

    def __add_padding_cls_sep(self, seq_list: list, sort: bool = False, pad_sign='[PAD]'):
        """
        add padding, cls and sep for sequence

        :param seq_list: sequence to be processed
        :param sort: if sort the sequences by length
        :param pad_sign: sign used to pad
        """

        len_list: list = [len(seq) for seq in seq_list]
        max_len: int = max(len_list)

        if sort:
            index_list: list = np.argsort(len_list)[::-1]
        else:
            index_list: list = list(range(0, len(len_list)))

        m_seq_list: list = []
        for index in index_list:
            m_seq_list.append(['[CLS]'])
            m_seq_list[-1].extend(deepcopy(seq_list[index]))
            m_seq_list[-1].extend(['[SEP]'])
            m_seq_list[-1].extend([pad_sign] * (max_len - len_list[index]))

        return m_seq_list

    def __expand_slot(self, nested_list):
        for item in nested_list:
            if isinstance(item, (list, tuple)):
                for sub_item in self.__expand_slot(item):
                    yield sub_item
            else:
                yield item
