import time
import socket
from Work_with_files.Work_with_files import *

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for i in range(3):
        sock.sendto(b'get_last_block_hash', ('192.168.175.128', 9090))
        time.sleep(0.5)
