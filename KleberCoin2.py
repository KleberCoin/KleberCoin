# -*- coding: utf-8 -*-
#Python 2.7

import hashlib
import datetime

def sha256(string):
    sha256 = hashlib.sha256()
    sha256.update(string)
    return sha256.hexdigest()

#On crée une classe d'objet pour nos blocs
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        #Variables internes à l'objet
        #Numéro du bloc
        self.index = index
        #Date de création
        self.timestamp = timestamp
        #Contenu du block
        self.data = data
        #Hash du bloc précédent
        self.previous_hash = previous_hash
        #Hash du bloc (voir la fonction hash_block)
        self.hash = self.hash_block()

    #Fonction permettant d'obtenir le hash du bloc à l'aide de la fonction sha256
    def hash_block(self):
        return sha256(str(self.index) +
                        str(self.timestamp) +
                        str(self.data) +
                        str(self.previous_hash))

#Fonction permettant de créer le premier bloc
def create_first_block(data):
    #Le premier bloc prends le numéro 0
    #On choisi "0" arbitrairement comme hash du précédent bloc | Cette valeur n'a pas d'importance.
    return Block(0,datetime.datetime.now(),data,"0")

#Fonction permettant la création d'un nouveau bloc prenant en entrée le contenu du nouveau bloc et la chaîne de bloc à laquelle on veut ajouter le nouveau bloc
def create_next_block(data, blockchain):
    return Block(len(blockchain.chain), datetime.datetime.now(), data, blockchain.chain[-1].hash)

class Blockchain:
    def __init__(self, first_block):
        self.chain = [first_block]

    def check_block_validity(self, block):
        if (block.hash == sha256(str(block.index) +
                            str(block.timestamp) +
                            str(block.data) +
                            str(self.chain[block.index - 1].hash))) and (block.index == self.chain[block.index - 1].index + 1):
            #print("Block is valid.")
            return True
        else:
            #print("Block is invalid.")
            return False

    def add_block(self, block):
        if self.check_block_validity(block):
            self.chain.append(block)
            print("Block #{} added.".format(block.index))

    def check_chain_integrity(self):
        marker = []
        for i in range(0,len(self.chain)):
            block = self.chain[i]
            #print(str(i) + " : " + str(block.index))
            if not self.check_block_validity(block):
                #print("Block {} not true".format(block.index))
                marker.append(block.index)
        if len(marker) != 0:
            print("Blockchain integrity compromised\nBlock {} invalid".format(marker))
        return marker

def create_new_blockchain(first_block):
    return Blockchain(first_block)

def main():
    #On crée le premier bloc
    firstBlock = create_first_block("Une nouvelle aventure!")
    #On crée notre blockchain
    blockchain = create_new_blockchain(firstBlock)
    #On ajoute 20 blocs à notre chaîne
    for i in range(0,20):
        blockchain.add_block(create_next_block("Un nouveau bloc! | Bloc #{}".format(i),blockchain))
    #On modifie le 3ème bloc de la chaîne
    blockchain.chain[2] = Block(0,datetime.datetime.now(),"Bloc modifié","0")
    #On vérifie l'intégrité de la chaîne
    invalidBlockList = blockchain.check_chain_integrity()

if __name__ == '__main__':
    main()
