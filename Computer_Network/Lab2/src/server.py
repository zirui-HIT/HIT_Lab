import _thread
from config import args
from util.device import Device

if __name__ == '__main__':
    send_device = Device(args.server_port_S, args.client_host,
                         args.client_port_R, args.protocol)
    recv_device = Device(args.server_port_R, args.client_host,
                         args.client_port_S, args.protocol)
    lock = _thread.allocate_lock()

    _thread.start_new_thread(send_device.send,
                             (args.data_path + "/server_data.txt", lock))
    recv_device.receive()

    while lock.locked():
        pass

    """
    send_device = Device(args.server_port_S, args.client_host,
                         args.client_port_R, args.protocol)
    send_device.send(args.data_path + "/server_data.txt")
    """
