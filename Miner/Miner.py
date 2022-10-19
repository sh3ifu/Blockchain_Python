import time
import random
import socket
import hashlib
from datetime import datetime

from Work_with_files import *


class Miner:
    def __init__(self):
        self.__ip_address, self.__port = self.__load_vars(gethostname=False)
        self.__sock = self.__get_sock()
        

    def __load_vars(self, gethostname=False):
        settings = read_from_file('../settings.json')
        ip_address = settings['ip_address']
        port = settings['port']

        if gethostname:
            ip_address = socket.gethostbyname(socket.gethostname())

        return ip_address, int(port)

    def __get_sock(self):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __get_transactions(self):
        transactions_list = []
        transactions_hashes_list = []
        
        self.__sock.sendto(b'get_mempool', (self.__ip_address, self.__port))
        transactions, addr = self.__sock.recvfrom(65506)        

        if len(transactions) == 0:           
            return transactions_list, transactions_hashes_list

        transactions = transactions.decode('utf-8').split('\n')        

        for transaction in transactions:
            transaction_hash = hashlib.sha256(transaction.encode('utf-8')).hexdigest()
            transaction = transaction.split(' ')                    

            sender = transaction[1]
            receiver = transaction[3]
            amount = transaction[5]            
            
            transaction = {transaction_hash: {"sender": sender, "receiver": receiver, "amount": amount}}
            transactions_list.append(transaction)
            transactions_hashes_list.append(transaction_hash)

        return transactions_list, transactions_hashes_list

    def __get_difficulty(self):
        self.__sock.sendto(b'get_difficulty', (self.__ip_address, self.__port))
        difficulty, addr = self.__sock.recvfrom(1024)

        return int(difficulty.decode('utf-8'))

    def __get_last_block_hash(self):
        self.__sock.sendto(b'get_last_block_hash', (self.__ip_address, self.__port))
        last_block_hash, addr = self.__sock.recvfrom(2048)

        return last_block_hash.decode('utf-8')

    def __random_shuffle_transactions(self, transactions_hashes):
        random.shuffle(transactions_hashes)
        return transactions_hashes

    def __mine_block(self, timestamp, pre_hash, difficulty, transactions_hashes):
        nonce = 0
        block_hash = timestamp + ' ' + pre_hash + ' ' + str(difficulty)

        for transaction_hash in transactions_hashes:
            block_hash += ' ' + transaction_hash

        for i in range(10**8):
            correct = True
            nonce += 1
            current_block_hash = hashlib.sha256(str(block_hash + ' ' + str(nonce)).encode('utf-8')).hexdigest()            

            for i in range(difficulty):
                if current_block_hash[i] != '0':
                    correct = False
            
            if correct:
                break

        if not correct:
            transactions_hashes = self.__random_shuffle_transactions(transactions_hashes)
            print('[RESHUFFLE]')
            self.__mine_block(timestamp, pre_hash, difficulty, transactions_hashes)


        return current_block_hash, nonce          

    def __create_block(self):
        transactions, transactions_hashes = self.__get_transactions()
        transactions_count = len(transactions)

        timestamp = datetime.now()
        timestamp = str(int(timestamp.timestamp()))

        difficulty = self.__get_difficulty()
        last_block_hash = self.__get_last_block_hash()

        print(last_block_hash)
                
        current_block_hash, nonce = self.__mine_block(timestamp, last_block_hash, difficulty, transactions_hashes)

        new_block = {current_block_hash: {
            "timestamp": timestamp,
            "nonce": str(nonce),
            "pre_hash": last_block_hash, 
            "difficulty": str(difficulty),
            "count": str(transactions_count),
            "transactions": transactions
        }}

        return str(new_block)

    def __send_block(self):
        block = bytes(self.__create_block(), 'utf-8')

        request = bytes(f'add_block\t{block}', 'utf-8')

        self.__sock.sendto(request, (self.__ip_address, self.__port))
        result, addr = self.__sock.recvfrom(65506)

        return result.decode('utf-8')

    def start_mining(self, delay):
        while True:
            result = self.__send_block()
            random_delay = random.randint(0, delay)
            current_date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            
            print(f'[{current_date}]\t{result}')
            
            time.sleep(random_delay)


if __name__ == '__main__':
    miner = Miner()
    delay = int(input('Delay: '))
    miner.start_mining(delay)
