#Python 2.7

import hashlib

import datetime as date


class Block:
    def __init__(self, timestamp, data, previous_block):
        self.index = previous_block.index + 1
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_block.hash
        self.hash = self.hash_block()

    def hash_block(self):
        sha256 = hashlib.sha256()
        sha256.update(str(self.index) +
                        str(self.timestamp) +
                        str(self.data) +
                        str(self.previous_hash))
        return sha256.hexdigest()

def create_first_block():
    return Block(0,datetime.datetime.now(),"First Block","0")


class Blockchain:
    def __init__(self, first_block):
        self.chain = [first_block]

    def check_block_validity(self, block):
        if block.hash == sha256(str(block.index) +
                            str(block.timestamp) +
                            str(block.data) +
                            str(self.chain[(block.index - 1].hash)):
            return True
        else:
            return False

    def add_block(self, block):
        if check_block_validity(block):
            self.chain.append()

    def check_chain_integrity(self):
        for block in self.chain:
            if not self.check_block_validity(block):
                print("Bloc {} not true".format(block.index))
