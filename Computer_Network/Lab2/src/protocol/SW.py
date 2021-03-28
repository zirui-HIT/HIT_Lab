import select
from typing import List
from config import args
from random import random
from util.data import Data

LOST_PACKET_RATIO = args.lost_packet_ratio


class SW(object):
    def __init__(self,
                 source_socket,
                 target_host,
                 target_port,
                 buffer_size=args.buffer_size,
                 delay_time=args.delay_time,
                 seq_size=2):
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
        self.__delay_time = delay_time
        self.__seq_size = seq_size

    def send(self, data_path, lock=None):
        """
        向目的主机发送数据

        :param data_path: 数据路径
        :param lock: 是否线程阻塞
        """
        if lock:
            lock.acquire()
        seq = 0
        last: Data = None
        f = open(data_path, 'r')

        while True:
            line = f.readline().strip()
            if not line:
                break

            last = Data(line, seq % self.__seq_size)
            seq += 1

            ack = -1
            clock = 0
            while ack != last.seq():
                if clock == self.__delay_time:
                    print("time out, try to resend")
                    self.__source_socket.sendto(
                        (str(last.seq()) + " " + last.message()).encode(),
                        self.__target)
                    clock = 0

                readable_list, writeable_list, errors = select.select([
                    self.__source_socket,
                ], [], [], 1)
                if len(readable_list) > 0:
                    try:
                        ack, address = self.__source_socket.recvfrom(
                            self.__buffer_size)
                        ack = int(ack.decode())
                    except BaseException:
                        print("occur ack exception")

                clock += 1

        f.close()
        self.__source_socket.close()
        if lock:
            lock.release()

    def receive(self) -> List[str]:
        """
        从目的主机接收数据
        """
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

                if random() > LOST_PACKET_RATIO:
                    self.__source_socket.sendto(
                        str(ack_seq).encode(), self.__target)

                    if message.split()[1] == "<EOF>":
                        return ret
                    print(message)
                    ret.append(message.split()[1])

        self.__source_socket.close()
