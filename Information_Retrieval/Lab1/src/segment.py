from utils.tokenizer import Tokenizer
from utils.base import Base

if __name__ == '__main__':
    base = Base.load_json('Lab1/data/result/craw.json')
    tokenizer = Tokenizer('Lab1/data/stopwords/stopwords(new).txt')

    base.tokenize(tokenizer)
    base.save_json('Lab1/data/result/segment.json')
