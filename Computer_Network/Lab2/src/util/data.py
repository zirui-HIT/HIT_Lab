from copy import deepcopy


STATE2CODE = {"NOT_SENT": 0, "SENT_NOT_ACKED": 1, "ACKED": 2}
CODE2STATE = {0: "NOT_SENT", 1: "SENT_NOT_ACKED", 2: "ACKED"}


class Data(object):
    def __init__(self, message: str, seq: int, state="NOT_SENT"):
        """
        数据段

        :param message: 数据段内容
        :param seq: 数据段序列号
        :param state: 数据段状态，默认为“未发送”
        """
        self.__message = deepcopy(message)
        self.__seq = seq
        self.__state = STATE2CODE[state]

    def message(self):
        return deepcopy(self.__message)

    def seq(self):
        return self.__seq

    def state(self):
        return CODE2STATE[self.__state]

    def switch(self, state: str):
        """
        将数据段的状态变更
        若状态变更不合法，则不修改，并抛出异常

        :param state: 目标状态
        """
        code = STATE2CODE[state]

        if self.__check_state(code):
            self.__state = code
        else:
            raise Exception("不合法的状态变更")

    def __check_state(self, state):
        if self.__state == 2 and state == 1:
            return False
        if self.__state == 0 and state == 2:
            return False
        return True
