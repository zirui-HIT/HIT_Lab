import socket

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 12138
    BUFFER_SIZE = 2048

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((HOST, PORT))
    print("client connect successfully")

    op = "GET http://www.bit.edu.cn HTTP/1.1\r\nHost: www.bit.edu.cn\r\nProxy-Connection: keep-alive\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36\r\n\r\n"
    while True:
        s = input("Input something:")
        if s == "Q":
            break
        else:
            clientSocket.send(op.encode())
            while True:
                message = clientSocket.recv(BUFFER_SIZE)
                if not message:
                    break
                print(message.decode('utf-8', 'ignore'))
