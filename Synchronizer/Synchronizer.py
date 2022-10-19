from FTP.FTP_client import FTPProtocol


class Synchronizer:
    def __init__(self, ip_address, port, username, password, is_send):
        self.__ip_address = ip_address
        self.__port = port
        self.__username = username
        self.__password = password
        self.__ftp = FTPProtocol(ip_address, port, is_send)

    def get_blockain(self):
        self.__ftp.get_file(self.__username, self.__password, filename='test.txt')

    def send_blockchain(self):
        self.__ftp.start_ftp_server(self.__username, self.__password)
