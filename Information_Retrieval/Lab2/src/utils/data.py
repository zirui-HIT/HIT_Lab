from typing import Dict
from typing import List
from copy import deepcopy


class DataManager(object):
    """数据处理集合

    Attributes:
        __name: 数据集名称
        __len: 数据数量
        __data: 存储数据
    """

    def __init__(self, name: str, data: List[Dict]):
        self.__name = name
        self.__len = len(data)
        self.__data = deepcopy(data)

    @staticmethod
    def load(name: str, path: str):
        """从json文件中加载数据

        Args:
            name: 数据集名称
            path: 数据路径
        """
        res = []

        import json
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                res.append(json.loads(line))

        if 'document' in res[0]:
            for i in range(len(res)):
                current = ""
                for d in res[i]['document']:
                    current = current + d
                res[i]['text'] = current

        return DataManager(name, res)

    def dump(self, path: str):
        """将数据保存到json文件

        Args:
            path: 数据路径
        """
        from utils.utils import save_json
        save_json(self.__data, path)

    def get(self, key: str) -> List:
        """提取键对应的属性

        Args:
            key: 属性

        Returns:
            查询属性
        """
        print('getting ' + self.__name + '--' + key)

        from tqdm import tqdm
        ret = []
        for d in tqdm(self.__data):
            ret.append(d[key])
        return ret

    def retrieval(self, key: str, question: List[List[float]], pid: List[int] = None):
        """从数据库中查找和问题最匹配的文档

        Args:
            key: 查询关键字
            question: 向量化的问题
            pid: 真实pid

        Returns:
            查找到的最匹配文档的pid
            若输入提供pid，则额外返回准确率
        """
        import numpy as np

        document = self.get(key)
        document = np.array(document)
        question = np.array(question)

        print("retrievaling pid")
        res = np.matmul(question, document.T)

        res = res.T
        for i in range(len(res)):
            d = np.linalg.norm(document[i])
            if d != 0:
                res[i] /= np.linalg.norm(document[i])
        res = res.T

        ans = []
        for i in range(len(res)):
            ans.append(int(np.argmax(res[i])))

        if pid is None:
            return ans

        cnt = 0
        for i in range(len(ans)):
            if ans[i] == pid[i]:
                cnt += 1
        return ans, cnt / len(ans)

    def delete(self, key: str):
        """刪除key對應的屬性

        Args:
            key: 刪除屬性
        """
        print('deleting ' + self.__name + '--' + key)
        from tqdm import tqdm
        for i in tqdm(range(self.__len)):
            self.__data[i].pop(key)

    def update(self, learner, key: List[str], value: str):
        """将key作为参数调用learner，将返回的结果保存到value中

        Args:
            learner: 学习器，必须声明predict
            key: 调用参数键
            value: 保存键
        """
        if isinstance(key, str):
            key = [key]

        print('updating ' + self.__name + '--' + value)
        res = self._call(learner, key)
        for i in range(self.__len):
            self.__data[i][value] = res[i]

    def _call(self, learner, key: List[str]):
        args_number = len(key)

        data = []
        for i in range(args_number):
            data.append(self.get(key[i]))

        if args_number == 1:
            return learner.predict(data[0])
        elif args_number == 2:
            return learner.predict(data[0], data[1])
        elif args_number == 3:
            return learner.predict(data[0], data[1], data[2])
