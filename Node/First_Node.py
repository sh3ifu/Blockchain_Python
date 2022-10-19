import socket
from datetime import datetime

from Blockchain.Blockchain import Blockchain
from Work_with_files.Work_with_files import *
from Synchronizer.Synchronizer import Synchronizer


class Node:
    def __init__(self):
        # IP address and port required to connect to the node
        self.__ip_address, self.__port = self.__load_vars(gethostname=False)
        # Network socket
        self.__sock = None
        # Flag indicating exit from the program
        self.__quit = False
        # The instance of the blockchain class
        self.__blockchain = Blockchain()
        # IP addresses of connected nodes
        self.__nodes_list = [self.__ip_address]

        self.__synchronizer = Synchronizer(self.__ip_address, 9091, username=self.__ip_address, password='bitcoin')

        # Node commands
        self.__commands = {
            'get_mempool': self.__blockchain.get_mempool,
            'get_difficulty': self.__blockchain.get_difficulty,
            'get_last_block_hash': self.__blockchain.get_last_block_hash,
            'add_transaction': self.__blockchain.add_transaction,
            'add_block': self.__blockchain.add_block,
            'create_node': print('New node connected!'),
        }

    # Loading values needed to working node
    def __load_vars(self, gethostname=False):
        # Reading settings from a file
        settings = read_from_file('settings.json')
        # Getting network parameters
        ip_address = settings['ip_address']
        port = settings['port']

        # If "gethostname" flag is True, means that the node will be launched on the local network
        if gethostname:
            ip_address = socket.gethostbyname(socket.gethostname())

        self.__print_sys_info('[Sys] Load vars')

        return ip_address, int(port)

    # Starting UDP server
    def __launch_server(self, ip_address, port):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind((ip_address, port))

        self.__print_sys_info('[ SERVER STARTED ]')

    # Parsing requests received from other network members
    def __parse_request(self, request, addr):
        request = request.split('\t')
        # res = None

        if request[0] not in self.__commands:
            self.__print_sys_info(f'[Error] Invalid request\nRequest = {request}, addr = {addr}')
            return

        if len(request) < 2:
            res = self.__commands[request[0]]()
        else:
            res = self.__commands[request[0]](request[1])

        if type(res) == str:
            self.__print_sys_info(res)
        elif type(res) == bytes:
            self.__sock.sendto(res, addr)
        elif type(res) == tuple:
            self.__sock.sendto(res[0], addr)
            self.__print_sys_info(res[1])

        # if request[0] == 'get_mempool':
        #     self.__get_mempool(addr)
        # elif request[0] == 'get_difficulty':
        #     self.__get_difficulty(addr)
        # elif request[0] == 'get_last_block_hash':
        #     self.__get_last_block_hash(addr)
        # elif len(request) < 2:
        #     self.__print_sys_info(f'[Error] Invalid request\nRequest = {request}, addr = {addr}')
        #     return
        # elif request[0] == 'add_transaction':
        #     self.__add_transaction(request[1])
        # elif request[0] == 'add_block':
        #     self.__add_block(request[1], addr)
        # else:
        #     self.__print_sys_info(f'[Error] Invalid request\nRequest = {request}, addr = {addr}')

    # Method print system info in node
    def __print_sys_info(self, mess):
        current_date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

        print(f'{current_date}\t{mess}')

    # The method that starts the node
    def start_node(self):
        self.__launch_server(self.__ip_address, self.__port)

        while not self.__quit:
            try:
                data, addr = self.__sock.recvfrom(65506)
                data = data.decode('utf-8')

                self.__parse_request(data, addr)

            except Exception as e:
                print(e)
                self.__print_sys_info('[ SERVER STOPPED ]')
                self.__quit = True

        self.__sock.close()
