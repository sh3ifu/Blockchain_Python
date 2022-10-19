import os
import socket
import threading

from ftplib import FTP
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


class FTPProtocol:
    def __init__(self, ip_address):
        # IP address and port needed to work with FTP protocol
        self.__ip_address = ip_address
        # self.__port = port

        # Creating UDP socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # if is_send:
        #     self.__sock.bind((self.__ip_address, port))

        # Variable that will store the FTP server
        self.__server = None

    # The "stop_ftp" command will be sent over the UDP protocol to stop the FTP server
    def __launch_udp_server(self):
        # Receive message from client
        data, addr = self.__sock.recvfrom(1024)

        # If client send "stop_ftp" command, then stop FTP server
        if data == b'stop_ftp':
            self.__server.close_when_done()
            return

    def __launch_ftp_server(self):

        authorizer = DummyAuthorizer()

        # Define a new user having full r/w permissions and a read-only
        # anonymous user
        # authorizer.add_user(username, password, '.', perm='elradfmwMT')
        authorizer.add_anonymous(os.getcwd())

        # Instantiate FTP handler class
        handler = FTPHandler
        handler.authorizer = authorizer

        # Instantiate FTP server class and listen on 0.0.0.0:2121
        address = (self.__ip_address, 21)
        self.__server = FTPServer(address, handler)

        # set a limit for connections
        self.__server.max_cons = 256
        self.__server.max_cons_per_ip = 5

        # start ftp server
        self.__server.serve_forever()

    # This method starts FTP and UDP servers
    def start_ftp_server(self):
        # Since the FTP server is blocking the thread, it and UDP run on different threads.
        ftp_thread = threading.Thread(target=self.__launch_ftp_server, args=())
        # udp_thread = threading.Thread(target=self.__launch_udp_server, args=())

        ftp_thread.start()
        # udp_thread.start()

    # This method is for downloading a file from an FTP server
    def get_file(self, filename='BlockchainData/Blockchain.json'):
        # Create FTP client
        ftp = FTP(self.__ip_address)

        # Login to FTP server
        ftp.login()

        # Send a download request for a file and then save it
        with open(filename, 'wb') as fp:
            ftp.retrbinary(f'RETR {filename}', fp.write)

        # Client disconnect from FTP server
        ftp.quit()

        # Send request to stop FTP server
        # request = b'stop_ftp'
        # self.__sock.sendto(request, (self.__ip_address, self.__port))
