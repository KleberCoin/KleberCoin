# -*- coding: utf-8 -*-
#Python 2.7

import hashlib

def sha256(string):
    sha256 = hashlib.sha256()
    sha256.update(string)
    return sha256.hexdigest()


class Block:
    def __init__(self, data, previous_hash):
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        return sha256(str(self.data) + str(self.previous_hash))


def create_first_block(data):
    return Block(data,"0")


def create_next_block(data, blockchain):
    return Block(data, blockchain.chain[-1].hash)


class Blockchain:
    def __init__(self, first_block):
        self.chain = [first_block]

    def check_block_validity(self, block, block_number):
        if (block.hash == sha256(str(block.data) +
                            str(self.chain[block_number - 1].hash))):
            return True
        else:
            return False

    def add_block(self, block):
        if self.check_block_validity(block, len(self.chain)):
            print("Block #{} added.".format(len(self.chain)))
            self.chain.append(block)

    def check_chain_integrity(self):
        marker = []
        for i in range(1,len(self.chain)):
            block = self.chain[i]
            if not self.check_block_validity(block, i):
                marker.append(i)
        if len(marker) != 0:
            print("Blockchain integrity compromised" + "\n" +
                "Block {} invalid".format(marker))
        return marker


def create_new_blockchain(first_block):
    return Blockchain(first_block)

def main():
    firstBlock = create_first_block("Une nouvelle aventure!")
    blockchain = create_new_blockchain(firstBlock)
    for i in range(0,20):
        blockchain.add_block(create_next_block("Un nouveau bloc!".format(i),
            blockchain))
    blockchain.chain[2] = Block("Bloc modifié","0")
    invalidBlockList = blockchain.check_chain_integrity()

if __name__ == '__main__':
    main()
