from typing import List
from transformers import BertTokenizer


class Tokenizer(object):
    def __init__(self):
        self.__tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

    def __call__(self, batch: List[List[str]]):
        """
        tokenize the batch

        :param batch: batch to be tokenized
        """
        cnt = len(batch)
        pieces: List[List[str]] = [[] for _ in range(cnt)]
        spans: List[List[int]] = [[] for _ in range(cnt)]

        for i in range(cnt):
            length = 0
            for j in range(len(batch[i])):
                word = batch[i][j]
                piece = self.__tokenizer.tokenize(word)

                pieces[i].extend(piece)
                spans[i].append((length, length + len(piece)))
                length += len(piece)

        return pieces, spans

    def piece2index(self, piece):
        """
        get index of piece

        :param piece: piece to be gotten
        """
        return self.__tokenizer.convert_tokens_to_ids(piece)
