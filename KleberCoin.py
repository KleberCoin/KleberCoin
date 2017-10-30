import hashlib

import datetime as date

def sha256(string_to_hash):

class Block:
    def __init__(self, timestamp, data, previous_block):
        self.index = previous_block.index + 1
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_block.hash
        self.hash = self.hash_block()

    def hash_block(self):
        string_to_hash(str(self.index) +
                        str(self.timestamp) +
                        str(self.data) +
                        str(self.previous_hash))
        return sha256(string_to_hash)

def creation_premier_bloc():
    return Block(0,datetime.datetime.now(),"Premier bloc","0")
