import hashlib
from datetime import datetime

from Work_with_files.Work_with_files import *


class Blockchain:
    def __init__(self):
        # Mining difficulty
        self.__difficulty = self.load_difficulty()
        # Block reward
        self.__reward = 50
        # Time of creation of the last block
        self.__last_block_timestamp = self.__get_last_block_timestamp()
        # Average time it takes to create a new block
        self.__block_time = 60
        # The count of transactions in block
        self._transactions_in_block = 200
        # The transactions themselves are combined in one line
        self.__transactions = ''

        # self.__sys_message = ''

    # Loading the difficulty of the last mined block
    def load_difficulty(self):
        blockchain = read_from_file('BlockchainData/Blockchain.json')
        blocks_hashes = list(blockchain.keys())
        last_block_difficulty = blockchain[blocks_hashes[-1]]['difficulty']

        self.__print_sys_info('[Sys] Get last block difficulty')
        return last_block_difficulty

    # Get time of creation of the last block
    def __get_last_block_timestamp(self):
        # Reading blockchain data from the corresponding file
        blockchain = read_from_file('BlockchainData/Blockchain.json', js=True)
        # Getting hashes of all blocks
        block_hashes = list(blockchain.keys())

        # Displaying system information about actions in a node
        # self.__print_sys_info('[Sys] Get last block timestamp')
        # Returning integer value of creation of the last block
        return int(blockchain[block_hashes[-1]]['timestamp'])

    # Getting transactions that are in the mempool and sending them to the miner
    def get_mempool(self):
        # Read transactions from file
        transactions = read_from_file('BlockchainData/mempool.txt', js=False, readlines=True)
        # Getting the required number of transactions
        transactions = transactions[:self._transactions_in_block]
        # Converting a string to bytes, since only they can be transmitted over the network
        transactions = bytes('\n'.join(transactions), 'utf-8')

        # Sending transactions to the miner
        return transactions, '[Request] Get mempool'

    # Method added new transactions, that was created by client
    def add_transaction(self, transaction):
        # Since all unmined transactions are in the mempool, which is stored as a file, in order not to constantly open
        # the file to write only one transaction (and there can be hundreds of them per second), they are all written
        # in one line, and when this line is long enough, only then transactions are written to file

        # Added transaction to string
        self.__transactions += (transaction + '\n')

        # If length of string transactions is enough(15000 is about 100 transactions long)
        # written it to file and clear string
        if len(self.__transactions) >= 15000:
            write_to_file(self.__transactions, 'mempool.txt')
            self.__transactions = ''
            return '[Request] Transactions added to mempool'

        return '[Request] Add transaction'

    # Since the miner is a separate member of the network that connects to it, he can act according to his own goals,
    # which may go against the general goals of the blockchain participants, and he can also act maliciously at all.
    # Therefore, each node running on the network is required to validate the blocks it receives so that other
    # participants cannot harm the network.
    def __block_validation(self, block):
        # Get the hash of the block that just arrived
        block_hash = str(list(block.keys()))[2:-2]

        # Get data from this block, such as: block creation time(timestamp), hash of the previous block(pre_hash),
        # difficulty, number of attempts spent on mining(nonce)
        timestamp = block[block_hash]['timestamp']
        pre_hash = block[block_hash]['pre_hash']
        difficulty = block[block_hash]['difficulty']
        nonce = block[block_hash]['nonce']

        # To check the correctness of the block sent by the miner, need to add all the block parameters
        # to the string, and then calculate its hash
        current_block_hash = timestamp + ' ' + pre_hash + ' ' + difficulty

        # Gettings hashes of all transactions in this block
        transactions_hashes = block[block_hash]['transactions']
        # Iterate through each transaction and add its hash to the current row
        for transaction_hash in transactions_hashes:
            transaction_hash = str(list(transaction_hash.keys()))[2:-2]
            current_block_hash += ' ' + transaction_hash

        # Calculating current block hash
        current_block_hash = hashlib.sha256(str(current_block_hash + ' ' + str(nonce)).encode('utf-8')).hexdigest()

        # If the calculated hash of the block is equal to what miner sent, then the block has passed the validation
        # and will be added to the blockchain
        if block_hash == current_block_hash:
            return True

        # If the block fails validation, it will not be added to the blockchain
        return False

    # A mechanism for changing the difficulty of mining, designed to adjust the block creation time so that it is
    # created on average in the same time
    def __change_difficulty(self, current_timestamp):
        # If the difference in time between the last created block and the current one is greater than the average time,
        # then that need to lower the complexity, if less then increase
        if ((current_timestamp - self.__last_block_timestamp) > self.__block_time) and (int(self.__difficulty) > 1):
            self.__difficulty = str(int(self.__difficulty) - 1)
            return '[Sys] Difficulty changed-'
        elif (current_timestamp - self.__last_block_timestamp) < self.__block_time:
            self.__difficulty = str(int(self.__difficulty) + 1)
            return '[Sys] Difficulty changed+'

    # Method for adding a new block to the blockchain if it passed the validation
    def add_block(self, block):
        # Uploading blockchain
        blockchain = read_from_file('BlockchainData/Blockchain.json', js=False)
        block = block[2:-1]
        block = block.replace('\'', '"')
        new_block = json.loads(block)

        if self.__block_validation(new_block):
            new_block = str(new_block)
            new_block = new_block[1:-1]
            new_block = new_block.replace('\'', '"')

            current_timestamp = int(datetime.now().timestamp())
            self.__last_block_timestamp = self.__get_last_block_timestamp()

            # If necessary, the difficulty of mining is changed
            is_difficulty_changed = self.__change_difficulty(current_timestamp)

            # The block is added to the blockchain
            blockchain = blockchain[:-1] + ',' + new_block + '\n}'
            write_to_file(blockchain, 'BlockchainData/Blockchain.json', mode='w')

            # Those transactions that were added to the block are removed from the mempool
            delete_in_file('BlockchainData/mempool.txt', self._transactions_in_block)

            mess = bytes(f'Block added successfully\nReward: {self.__reward}', 'utf-8')
            return mess, f'[Request] Add block\n[Sys] Block validation success\n{is_difficulty_changed}\n' \
                         f'[Sys] Reward successfully sended'
        # If the block is not validated, it is not added to the blockchain
        else:
            return b'Error adding block', '[Request] Add block\n[Sys] Block validation unsuccess'

    # Method returns difficulty
    def get_difficulty(self):
        difficulty = bytes(self.__difficulty, 'utf-8')
        return difficulty, '[Request] Get difficulty'

    # Method returns hash of the last mined block
    def get_last_block_hash(self):
        blockchain = read_from_file('BlockchainData/Blockchain.json')
        blocks = list(blockchain.keys())
        last_block_hash = bytes(str(blocks[-1]), 'utf-8')

        return last_block_hash, '[Request] Get last block hash'

    # Method print system info in node
    def __print_sys_info(self, mess):
        current_date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

        print(f'{current_date}\t{mess}')
