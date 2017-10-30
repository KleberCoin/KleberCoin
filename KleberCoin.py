import hashlib

import datetime as date

class Block:
    def __init__(self, index, timestamp, data, previous_block):
        self.index = index
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

def creation_premier_bloc():
    return Block(0,datetime.datetime.now(),"Premier bloc","0")
