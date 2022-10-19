import os
import time
import json
import click
import socket
import random
from datetime import datetime

from Work_with_files import *


class Client:
    def __init__(self):
        self.__ip_address, self.__port = self.__load_vars(gethostname=False)        
        self.__sock = self.__get_sock()

    # def __del__(self):
    #     self.__sock.close()

    def __load_vars(self, gethostname=False):
        settings = read_from_file('D:\\Projects\\Python\\BlockchainPython\\Node_settings\\settings.json')
        ip_address = settings['ip_address']
        port = settings['port']

        if gethostname:
            ip_address = socket.gethostbyname(socket.gethostname())

        return ip_address, int(port)
    
    def __get_sock(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __send_transaction(self, transaction):
        request = bytes(f'add_transaction\t{transaction}', 'utf-8')
        self.__sock.sendto(request, (self.__ip_address, self.__port))

    def __generate_address(self):
        address = ''
        regex = ":;<=>?@[]/_-^\`"

        while len(address) < 42:
            f = False
            symb = chr(random.randint(48, 122))

            for i in regex:
                if i == symb:
                    f = True
            
            if not f:
                address += symb

        return address

    def __create_transaction(self):
        sender_address = self.__generate_address()
        receiver_address = self.__generate_address()
        amount = str(random.randint(0, 100000) / 1000)

        transaction = f'SENDER {sender_address} RECEIVER {receiver_address} AMOUNT {amount}'

        return transaction

    def start_generating_transactions(self, delay):
        while True:
            random_delay = random.randint(0, delay)
            transaction = self.__create_transaction()
            current_date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

            print(f'{transaction}\t{current_date}')
            self.__send_transaction(transaction)

            time.sleep(random_delay)


if __name__ == '__main__':
    click.clear()

    client = Client()

    delay = int(input('Delay: '))

    client.start_generating_transactions(delay)
