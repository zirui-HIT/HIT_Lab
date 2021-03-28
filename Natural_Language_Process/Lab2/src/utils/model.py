from typing import List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import BertModel


class BertRecognizer(nn.Module):
    def __init__(self, slot_vocab_size: int, dropout_rate: float):
        super(BertRecognizer, self).__init__()
        self.__encoder = BertEncoder(dropout_rate)
        self.__decoder = LinearDecoder(BertEncoder.encoder_dim,
                                       slot_vocab_size)
        self.__piece2word = Piece2Word()

    def forward(self, piece_tensor: torch.Tensor, piece_mask,
                span_list: List[List[Tuple[int, int]]]):
        hidden = self.__encoder(piece_tensor, piece_mask)

        span_tensor_list = [[
            self.__piece2word(hidden[[sent_i], span[0] + 1:span[1] + 1, :])
            for span in span_list[sent_i]
        ] for sent_i in range(len(span_list))]

        len_list = self.__padding(span_tensor_list,
                                  torch.zeros((1, 1, hidden.size(2))))

        padded_tenor = torch.cat([
            torch.cat(span_tensor_list[sent_i], dim=1)
            for sent_i in range(len(span_list))
        ],
            dim=0)

        slot_tensor = self.__decoder(padded_tenor)

        return torch.cat(
            [slot_tensor[i][:len_list[i], :] for i in range(0, len(len_list))],
            dim=0)

    @staticmethod
    def __padding(seq_list: List[List[torch.Tensor]], pad_sign):
        len_list: list = [len(seq) for seq in seq_list]
        max_len: int = max(len_list)

        if torch.cuda.is_available():
            pad_sign = pad_sign.cuda()

        for seq_i in range(len(len_list)):
            seq_list[seq_i].extend([pad_sign] * (max_len - len_list[seq_i]))

        return len_list


class BertEncoder(nn.Module):
    # from pretrained
    num_layer = 12
    encoder_dim = 768

    def __init__(self,
                 dropout_rate: float,
                 model_type: str = "bert-base-uncased"):
        super(BertEncoder, self).__init__()
        self.__model = BertModel.from_pretrained(model_type)
        self.__dropout = nn.Dropout(dropout_rate)

    def forward(self, piece_tensor: torch.LongTensor, mask):
        hidden = self.__model(piece_tensor, attention_mask=mask)[0]
        hidden = self.__dropout(hidden)

        return hidden


class LinearDecoder(nn.Module):
    def __init__(self, input_dim: int, output_dim: int):
        super(LinearDecoder, self).__init__()
        self.__linear_layer = nn.Linear(input_dim, output_dim)

    def forward(self, hidden):
        return F.log_softmax(self.__linear_layer(hidden), dim=-1)


class Piece2Word(nn.Module):
    def __init__(self):
        super(Piece2Word, self).__init__()

    def forward(self, input_tensor):
        return self._first(input_tensor)

    @staticmethod
    def _first(input_tensor):
        return input_tensor[:, 0, :].view(1, 1, -1)

    @staticmethod
    def _average(input_tensor):
        return torch.mean(input_tensor, dim=1, keepdim=True)

    @staticmethod
    def _sum(input_tensor):
        return torch.sum(input_tensor, dim=1, keepdim=True)
