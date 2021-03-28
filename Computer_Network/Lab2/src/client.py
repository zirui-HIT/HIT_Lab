import _thread
from config import args
from util.device import Device

if __name__ == '__main__':
    send_device = Device(args.client_port_S, args.server_host,
                         args.server_port_R, args.protocol)
    recv_device = Device(args.client_port_R, args.server_host,
                         args.server_port_S, args.protocol)
    lock = _thread.allocate_lock()

    _thread.start_new_thread(send_device.send,
                             (args.data_path + "/client_data.txt", lock))
    recv_device.receive()

    while lock.locked():
        pass
    
    """
    recv_device = Device(args.client_port_R, args.server_host,
                         args.server_port_S, args.protocol)
    text = recv_device.receive()

    with open(args.receive_path, 'w') as f:
        for line in text:
            f.write(line + '\n')
    """
