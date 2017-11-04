# -*- coding: utf-8 -*-
#Python 2.7

import hashlib

#Pour plus de simplicité, on crée une fonction qui appelle la fonction sha256
#de la librairie 'hashlib'
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

#On crée une classe d'objet pour notre blockchain
class Blockchain:
    def __init__(self, first_block):
        #La classe Blockchain possède pour attribut une liste contenant les blocs
        self.chain = [first_block]

    #Méthode permettant de vérifier la validité d'un bloc
    def check_block_validity(self, block, block_number):
        #On test si le hash du bloc correspond à celui de la chaîne de caractère
        # contenant son contenu et le hash du bloc précédent de la chaîne.
        if (block.hash == sha256(str(block.index) +
                            str(block.timestamp) +
                            str(block.data) +
                            str(self.chain[block_number - 1].hash))) and (block.index == self.chain[block_number - 1].index + 1):
            #print("Block is valid.")
            #Si l'égalité se vérifie, le bloc est valide
            return True
        else:
            #print("Block is invalid.")
            #Si l'agalité ne se vérifie pas, le bloc est non valide
            return False

    #Méthode permettant l'ajout d'un bloc à la chaîne
    def add_block(self, block):
        #On ne permet l'ajout d'un bloc que si sa validité est affirmée par la
        # methode check_block_validity
        if self.check_block_validity(block, len(self.chain)):
            print("Block #{} added.".format(len(self.chain)))
            self.chain.append(block)

    #Méthode permettant de vérifier l'intégrité de la blockchain; si tous les
    #blocs sont valides
    def check_chain_integrity(self):
        #On crée une variable pour contenir la position dans la chaîne des blocs
        # non valides
        marker = []
        #On vérifie tous les blocs sauf le premier de la liste, le bloc 0 car ce
        # dernier est toujours valide
        #(aucun bloc ne le précède donc il ne dépend d'aucune information
        #provenant d'un autre bloc)
        marker = []
        #On vérifie tous les blocs sauf le premier de la liste, le bloc 0 car ce
        # dernier est toujours valide
        #(aucun bloc ne le précède donc il ne dépend d'aucune information
        #provenant d'un autre bloc)
        for i in range(1,len(self.chain)):
            block = self.chain[i]
            if not self.check_block_validity(block, i):
                marker.append(i)
        if len(marker) != 0:
            print("Blockchain integrity compromised" + "\n" +
                "Block {} invalid".format(marker))
        return marker

#Fonction permettant de créer une nouvelle blockchain à partir d'un bloc
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
