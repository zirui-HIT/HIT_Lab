import select
from util.data import Data
from typing import List
from config import args
from copy import deepcopy
from random import random

LOST_PACKET_RATIO = args.lost_packet_ratio


class SR(object):
    def __init__(self,
                 source_socket,
                 target_host,
                 target_port,
                 buffer_size=args.buffer_size,
                 delay_time=args.delay_time,
                 window_size=10,
                 seq_size=16):
        """
        初始化传输协议

        :param source_socket: 源主机socket
        :param target_host: 目的主机host
        :param buffer_size: buffer大小
        :param window_size: 滑动窗口大小
        :param seq_size: seq范围
        :param delay_time: 超时时间
        """
        self.__source_socket = source_socket
        self.__target = (target_host, target_port)
        self.__buffer_size = buffer_size
        self.__window_size = window_size
        self.__seq_size = seq_size
        self.__delay_time = delay_time

    def send(self, data_path: str, lock=None):
        """
        向目的主机发送数据

        :param data_path: 数据路径
        :param lock: 是否线程阻塞
        """
        if lock:
            lock.acquire()

        seq = 0
        clock = 0
        window: List[Data] = []
        f = open(data_path, 'r')

        while True:
            # 超时
            if clock > self.__delay_time:
                print("time out, try to resend")
                for data in window:
                    if data.state() == "SENT_NOT_ACKED":
                        data.switch("NOT_SENT")
                clock = 0

            # 添加传输数据
            while len(window) < self.__window_size:
                line = f.readline().strip()
                if not line:
                    break
                window.append(Data(line, seq % self.__seq_size))
                seq += 1

            # 传输完毕
            if not window:
                break

            # 开始传输
            for data in window:
                if data.state() == "NOT_SENT":
                    self.__source_socket.sendto(
                        (str(data.seq()) + " " + data.message()).encode(),
                        self.__target)
                    data.switch("SENT_NOT_ACKED")

            # 接收传输应答
            readable_list, writeable_list, errors = select.select([
                self.__source_socket,
            ], [], [], 1)
            if len(readable_list) > 0:
                try:
                    ack, address = self.__source_socket.recvfrom(
                        self.__buffer_size)
                    ack = int(ack.decode())

                    for data in window:
                        if ack == data.seq():
                            clock = 0
                            data.switch("ACKED")
                            break
                except BaseException:
                    print("occur ack exception")
            else:
                clock += 1

            # 窗口后移
            while len(window) > 0 and window[0].state() == "ACKED":
                window.pop(0)

        # 传输终止包
        seq = 0
        clock = 0
        while seq == 0:
            # 超时重传
            if clock == 0:
                self.__source_socket.sendto("-1 <EOF>".encode(), self.__target)

            # 接受传输应答
            readable_list, writeable_list, errors = select.select([
                self.__source_socket,
            ], [], [], 1)
            if len(readable_list) > 0:
                try:
                    ack, address = self.__source_socket.recvfrom(
                        self.__buffer_size)
                    seq = int(ack.decode())
                except BaseException:
                    print("occur ack exception")
            else:
                clock += 1

        f.close()
        self.__source_socket.close()
        if lock:
            lock.release()

    def receive(self):
        """
        从目的主机接收数据
        """
        ret = []
        window = [None] * self.__seq_size
        current_ack = 0

        while True:
            readable_list, writeable_list, errors = select.select([
                self.__source_socket,
            ], [], [], 1)
            if len(readable_list) > 0:
                message, address = self.__source_socket.recvfrom(
                    self.__buffer_size)
                message = message.decode()
                ack_seq = int(message.split()[0])

                if random() > LOST_PACKET_RATIO:
                    self.__source_socket.sendto(
                        str(ack_seq).encode(), self.__target)

                    if message.split()[0] == "-1":
                        return ret
                    elif message.split()[1] != "<EOF>":
                        window[ack_seq] = deepcopy(message.split()[1])
                        print(message)

                        while window[current_ack] is not None:
                            ret.append(window[current_ack])
                            window[current_ack] = None
                            current_ack = (current_ack + 1) % self.__seq_size

        self.__source_socket.close()
