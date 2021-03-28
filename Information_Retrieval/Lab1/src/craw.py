from utils.base import Base
import sys

if __name__ == "__main__":
    sys.setrecursionlimit(1000)

    base = Base.load_url('http://jwc.hit.edu.cn/', 'Lab1/data/attachment',
                         1000)

    base.save_json('Lab1/data/result/craw.json')
