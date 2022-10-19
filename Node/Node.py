import socket
from datetime import datetime

from Blockchain.Blockchain import Blockchain
from Work_with_files.Work_with_files import *
from FTP.FTP_client import FTPProtocol


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

        # Flag indicating whether the node has already synchronized with the blockchain
        self.__is_synchronized = False
        # Launching an FTP server, which is needed so that other nodes can connect and synchronize
        self.__ftp_server_launch()

        # IP addresses of connected nodes
        self.__nodes = [self.__ip_address]

        # Node commands
        self.__commands = {
            'get_mempool': self.__blockchain.get_mempool,
            'get_difficulty': self.__blockchain.get_difficulty,
            'get_last_block_hash': self.__blockchain.get_last_block_hash,
            'add_transaction': self.__blockchain.add_transaction,
            'add_block': self.__blockchain.add_block,
            'add_new_node': self.__add_new_node,
            'print_nodes': self.__print_nodes,
        }

    def __print_nodes(self):
        print(self.__nodes)

    def __ftp_server_launch(self):
        ftp = FTPProtocol(self.__ip_address)
        ftp.start_ftp_server()

    def __add_new_node(self, ip_address):
        self.__nodes.append(ip_address)
        self.__print_sys_info('[Sys] New node added')

    def __synch_node(self, ip_to_synch):
        ftp_client = FTPProtocol(ip_to_synch)
        ftp_client.get_file()

        for node in self.__nodes:
            self.__sock.sendto(b'add_new_node', (node, self.__port))

        self.__is_synchronized = True

    # Loading values needed to working node
    def __load_vars(self, gethostname=False):
        # Reading settings from a file
        settings = read_from_file('Blockchain_settings/settings.json')
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

    # Method print system info in node
    def __print_sys_info(self, mess):
        current_date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

        print(f'{current_date}\t{mess}')

    # The method that starts the node
    def start_node(self, ip_to_synch):
        # Launch UDP server
        self.__launch_server(self.__ip_address, self.__port)

        # Synchronize node with other nodes in blockchain
        self.__synch_node(ip_to_synch)

        while not self.__quit:
            try:
                # If node is not yet synchronized with the blockchain, then do not accept requests
                if not self.__is_synchronized:
                    continue
                data, addr = self.__sock.recvfrom(65506)
                data = data.decode('utf-8')

                self.__parse_request(data, addr)

            except Exception as e:
                print(e)
                self.__print_sys_info('[ SERVER STOPPED ]')
                self.__quit = True
        
        self.__sock.close()
