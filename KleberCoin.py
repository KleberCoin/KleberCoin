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
        sha256.update(bytes(str(self.index)"utf-8") +
                        bytes(str(self.timestamp)"utf-8") +
                        bytes(str(self.data)"utf-8") +
                        bytes(str(self.previous_hash)"utf-8"))
        return sha256.hexdigest()

def creation_premier_bloc():
    return Block(0,datetime.datetime.now(),"Premier bloc","0")


class Blockchain:
    def __init__(self, first_block):
        self.chain = [first_block]

    def add_block(self, block):
        if block.hash == sha256(str(block.index) +
                            str(block.timestamp) +
                            str(block.data) +
                            str(self.chain[-1].hash)):
            self.chain.append()
