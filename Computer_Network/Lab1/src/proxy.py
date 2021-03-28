import os
import time
import socket
import threading
import urllib.parse as urlparse


class Proxy(object):
    def __init__(self, port: int, listen: int, buffer: int):
        """
        创建代理服务器

        :param port: 代理服务器的端口号
        :param listen: 最大连接数
        :param buffer: 接收的最大数据量
        """
        self.__port = port
        self.__buffer = buffer
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__cache_path = "../cache"

        self.__socket.bind(('', port))
        self.__socket.listen(listen)

        # 若缓存路径不存在，则创建之
        if not os.path.exists(self.__cache_path):
            os.mkdir(self.__cache_path)

    def accept(self):
        """
        获取客户端的socket及连接请求
        """
        return self.__socket.accept()

    def __filter_user(self, address, path="../data/filter_user.txt"):
        """
        检查一个源主机是否要被过滤

        :param address: 源主机地址
        :param path: 过滤用户清单
        """
        with open(path, "r") as f:
            for line in f:
                if str(line) == str(address[0]):
                    return True
        return False

    def __filter_web(self, web, path="../data/filter_web.txt"):
        """
        检查一个网页是否要被过滤

        :param web: 待检查网址
        :param path: 过滤网址清单
        """
        with open(path, "r") as f:
            for line in f:
                if line == web:
                    return True
        return False

    def __fish(self, web, path="../data/fish.txt"):
        """
        检查一个网站是否需要被引导到另一个网站

        :param web: 待检查网址
        :param path: 引导网址清单
        """
        with open(path, "r") as f:
            for line in f:
                w = line.split()
                if w[0] == web:
                    return w[1]
        return None

    def connect(self, client: socket.socket, address: str):
        """
        通过代理服务器连接到指定地址

        :param client: 客户端socket
        :param address: 源主机地址
        """
        # 提取请求的信息
        message = client.recv(self.__buffer).decode('utf-8', 'ignore')
        headers = message.split('\r\n')
        request = headers[0].strip().split()
        # 若请求不完整，则直接结束；否则，使用urlparse解析请求的信息
        if len(request) < 1:
            print("Request Line not contains url!")
            print("Full Request Message:", message)
            client.close()
            return
        else:
            url = urlparse.urlparse(request[1][:-1] if request[1][-1] ==
                                    '/' else request[1])

        # 检查IP地址和网址是否要被过滤
        if self.__filter_user(address):
            client.send("Illegal user".encode())
            client.close()
            return
        if self.__filter_web(url.hostname):
            client.send("Illegal web".encode())
            client.close()
            return

        # 检查网址是否需要重定向，若需要，则更换原请求中所有的原地址，并重新解析
        fish = self.__fish(url.hostname)
        if fish is not None:
            message = message.replace(url.hostname, fish)
            headers = message.split('\r\n')
            request = headers[0].strip().split()
            url = urlparse.urlparse(request[1][:-1] if request[1][-1] ==
                                    '/' else request[1])

        # 开始检查cache是否存储在和是否被修改
        cache_path = self.__cache_path + '/' + \
            (url.hostname + url.path).replace('/', '_')
        cache_exist = os.path.exists(cache_path)
        cache_modified = False
        # 若缓存文件存在
        if cache_exist:
            # 构建新的请求报文，即在第二行插入If-Modified-Since
            temp = headers[0] + '\r\n'
            cache_time = os.stat(cache_path).st_mtime
            temp += 'If-Modified-Since: ' + time.strftime(
                '%a, %d %b %Y %H:%M:%S GMT', time.gmtime(cache_time)) + '\r\n'
            for line in headers[1:]:
                temp += line + '\r\n'

            # 创建向目标服务器连接的套接字，并发送请求
            cache_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cache_socket.connect((url.hostname, url.port if url.port else 80))
            cache_socket.sendall(str.encode(temp))

            # 若返回信息的状态码为304，表明缓存已经是最新的，直接发送之
            data = cache_socket.recv(self.__buffer)
            if data.decode('iso-8859-1').split()[1] == '304':
                print("load from cache")
                client.send(open(cache_path, 'rb').read())
            else:
                # 否则，进入缓存不存在的处理过程
                cache_modified = True

        if cache_exist is False or cache_modified:
            print("Attempt to connect " + url.geturl())

            # 创建连接目标服务器的套接字，并打开缓存文件
            target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target.connect((url.hostname, url.port if url.port else 80))
            target.sendall(message.encode())
            cache = open(cache_path, 'wb')

            while True:
                # 只要获取的buffer不为空，则一直获取
                buff = target.recv(self.__buffer)
                if not buff:
                    # 表明获取完毕，关闭套接字
                    cache.close()
                    target.close()
                    break
                # 将获得的信息写入缓存，并发送给客户端
                cache.write(buff)
                client.send(buff)
            client.close()


if __name__ == "__main__":
    # 创建套接字
    proxy = Proxy(12138, 10, 2048)
    while True:
        client_socket, address = proxy.accept()
        threading.Thread(target=proxy.connect,
                         args=(client_socket, address)).start()
