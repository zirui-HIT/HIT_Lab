import select
from util.data import Data
from typing import List
from random import random
from config import args

LOST_PACKET_RATIO = args.lost_packet_ratio


class GBN(object):
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
                clock = 0
                for data in window:
                    data.switch("NOT_SENT")

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

                    for i in range(len(window)):
                        if ack == window[i].seq():
                            clock = 0
                            window = window[i + 1:]
                            break
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
        last_ack = self.__seq_size - 1
        window = []
        ret = []

        while True:
            readable_list, writeable_list, errors = select.select([
                self.__source_socket,
            ], [], [], 1)
            if len(readable_list) > 0:
                message, address = self.__source_socket.recvfrom(
                    self.__buffer_size)
                message = message.decode()
                ack_seq = int(message.split()[0])

                if last_ack == (ack_seq - 1) % self.__seq_size:
                    if random() < LOST_PACKET_RATIO:
                        continue

                    self.__source_socket.sendto(
                        str(ack_seq).encode(), self.__target)
                    last_ack = ack_seq

                    if ack_seq not in window:
                        window.append(ack_seq)

                        if message.split()[1] == "<EOF>":
                            return ret

                        print(message)
                        ret.append(message.split()[1])
                    while len(window) > self.__window_size:
                        window.pop(0)
                else:
                    self.__source_socket.sendto(
                        str(last_ack).encode(), address)

        self.__source_socket.close()
