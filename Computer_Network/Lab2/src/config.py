import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--data_path',
                    '-dp',
                    type=str,
                    default="../data",
                    help="传输数据路径")
parser.add_argument('--receive_path',
                    '-rp',
                    type=str,
                    default="../recv/client_recv.txt",
                    help="接收数据路径")

parser.add_argument('--client_host',
                    '-ch',
                    type=str,
                    default="127.0.0.1",
                    help="客户端IP")
parser.add_argument('--server_host',
                    '-sh',
                    type=str,
                    default="127.0.0.1",
                    help="服务器IP")
parser.add_argument('--client_port_S',
                    '-cps',
                    type=int,
                    default=10240,
                    help="客户端作为发送方时的端口号")
parser.add_argument('--client_port_R',
                    '-cpr',
                    type=int,
                    default=10241,
                    help="客户端作为接收方时的端口号")
parser.add_argument('--server_port_S',
                    '-sps',
                    type=int,
                    default=10242,
                    help="服务器作为发送方时的端口号")
parser.add_argument('--server_port_R',
                    '-spr',
                    type=int,
                    default=10243,
                    help="服务器作为接收方时的端口号")

parser.add_argument('--buffer_size',
                    '-bf',
                    type=int,
                    default=1024,
                    help="buffer大小")
parser.add_argument('--delay_time', '-dt', type=int, default=3, help="超时时间")
parser.add_argument('--lost_packet_ratio',
                    '-lpr',
                    type=float,
                    default=0.2,
                    help="丢包率")

parser.add_argument('--protocol', '-p', type=str, default="SR", help="传输协议")

parser.add_argument('--random_seed', '-rs', type=int, default=0, help="随机数种子")

args = parser.parse_args()
