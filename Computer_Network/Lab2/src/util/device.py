from typing import List


class Device(object):
    def __init__(self, port, target_host, target_port, protocol):
        """
        一个与另一设备相连的设备

        :param port: 该设备的端口号
        :param target_host: 目标设备的IP地址
        :param protocol_kind: 传输协议，应与另一设备保持一致
        """
        import socket
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind(('', port))

        if protocol == "GBN":
            from protocol.GBN import GBN
            self.__protocol = GBN(self.__socket, target_host, target_port)
        if protocol == "SR":
            from protocol.SR import SR
            self.__protocol = SR(self.__socket, target_host, target_port)
        if protocol == "SW":
            from protocol.SW import SW
            self.__protocol = SW(self.__socket, target_host, target_port)

    def send(self, data_path: str, lock=None):
        """
        向另一设备发送数据

        :param data: 待发送数据地址
        :param lcok: 是否线程阻塞
        """
        self.__protocol.send(data_path, lock)

    def receive(self) -> List[str]:
        """
        从另一设备接收数据
        """
        return self.__protocol.receive()
