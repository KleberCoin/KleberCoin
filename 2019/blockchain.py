
# -*- coding: utf-8 -*-

"""
TODO

rémunération mineur ? --> non car ce qui va pousser les gens à miner c est leur possession de coins --> déflationiste
mise à jour diff
frais transactions ? --> non
"""

"""
Created on Fri Feb  8 10:31:07 2019
"""

import hashlib
from Crypto.PublicKey import RSA

import datetime

à_vérifier = {}
invalides = []
valides = []


class Bloc:
    def __init__(self, date, données, index_précédent, marquage_précédent):
        self.index = index_précédent + 1
        self.horodatage = date
        self.données = données
        self.marquage_précédent = marquage_précédent
        self.nonce = 0
        self.cible = 1  # entre 0 et 64 |mettre dans le sérialiseur https://en.bitcoin.it/wiki/Difficulty
        self.marquage = self.concassage()
        
    def concassage(self):
        sha256 = hashlib.sha256()
        sha256.update(bytes(str(self.index),"utf-8") +
                        bytes(str(self.horodatage),"utf-8") +
                        bytes(str(self.données),"utf-8") +
                        bytes(str(self.marquage_précédent),"utf-8") +
                        bytes(str(self.cible),"utf-8"))
        return sha256.hexdigest()
        
    def compte_0(self):
        i = 0
        while self.marquage[i] == "0":
            i +=1
        return i   
    
    def mine(self):
        while compte_0() < self.cible:
            self.nonce += 1
            self.marquage = self.concassage()
        

def création_premier_bloc():
    return Bloc(datetime.datetime.now(), "Premier bloc", -1, "Premier bloc")
        
class Chaine_de_Blocs:
    def __init__(self, *premier_bloc):
        self.chaine = [ *premier_bloc ]
        
    def vérification_de_chaine(self):
        invalides = []
        for bloc in self.chaine:
            if not self.vérification_de_bloc(bloc):
                invalides += bloc.index
                
        return invalides

    # Traitement d'un nouveau bloc
    def vérification_de_bloc(self, bloc):
        if bloc.marquage_précédent != self.chaine[-1].marquage or \
            bloc.marquage != bloc.concassage() or \
            bloc.index != 1 + self.chaine[-1].index :
            return False
            
        à_vérifier = {}
        invalides = []
        valides = []
    
        for transaction in bloc.données:
            if transaction.est_signée() and not transaction.émetteur in invalides:
                if transaction.émetteur in à_vérifier:
                    à_vérifier[transaction.émetteur] += - transaction.montant
                else : à_vérifier[transaction.émetteur] = - transaction.montant
            else :
                invalides += [transaction.émetteur]
        
        
        n = (bloc.index - 1)
        self.vérification_des_transactions(à_vérifier, valides, invalides, n )
        
        #print("Valides : ", valides)
        #print("Invalides : ", invalides )
        
        if len(invalides) == 0:
            return True
        else : return False
        
            
    # Fonction qui trie les demandes de transfert de fonds contenues dans le
    # dictionnaire
    def vérification_des_transactions(self, à_vérifier, valides, invalides, n):
        """
            Fonction qui trie les demandes de transferts de fonds contenues 
            dans le dictionnaire "à_vérifié" en ne considérant la chaîne de
            blocs que jusqu'au bloc d'inex n.
            Elle modifie la liste "valides" des émetteurs ayant les fonds
            nécessaires et la liste "invalides" des émetteurs ne les ayant
            pas.
        """
        for transaction in self.chaine[n].données:
            if transaction.émetteur in à_vérifier:
                à_vérifier[transaction.émetteur] -= transaction.montant
            elif transaction.destinataire in à_vérifier:
                    à_vérifier[transaction.destinataire] += transaction.montant
                    if à_vérifier[transaction.destinataire] >= 0:
                        del(à_vérifier[transaction.destinataire])
                        valides += [transaction.destinataire]
                    
        if len(list(à_vérifier)) !=0 and n > 1:
            vérification_des_transactions(à_vérifier, valides, invalides, (n-1))
        else : invalides += list(à_vérifier)

        
    
    def ajout_de_block(self, données):
        bloc = Bloc(datetime.datetime.now(), données, self.chaine[-1].index, self.chaine[-1].marquage)
        if self.vérification_de_bloc(bloc):
            self.chaine.append(bloc)
        """if bloc.index % (14*24*60*6) == 0 :
            décalage = 14 - (self.chaine[-1].date - self.chaine[bloc.index - 14*24*60*6].date).days
            if décalage < -7:
                bloc.cible = self.chaine[-1].cible - 1
            elif décalage > 7:
                bloc.cible = self.chaine[-1].cible - 1
        """


class Transaction:
    def __init__(self, émetteur, destinataire, montant, signature):
        self.émetteur = émetteur
        self.destinataire = destinataire
        self.montant = montant
        self.marquage = self.concassage()
        self.signature = signature
    
    def concassage(self):
        sha256 = hashlib.sha256()
        sha256.update(bytes(self.émetteur,"utf-8") +
                      bytes(self.destinataire,"utf-8") +
                      bytes(str(self.montant),"utf-8"))
        return sha256.hexdigest()
    
    def est_signée(self):
        clef = importer_clef_publique( self.émetteur )
        signature = clef.decrypt( bytes.fromhex( self.signature ) )
        if signature.decode() == self.concassage():
            return True
        else : return False
        

class Utilisateur:
    def __init__(self, clef_privée, clef_publique):
        self.clef_privée = clef_privée
        self.clef_publique = clef_publique
        
    def envoyer(self, destinataire, montant):
        # à relier au réseau
        transaction = Transaction( self.clef_publique, destinataire, montant, "0" )
        clef = importer_clef_privée(self.clef_privée)
        signature = clef.encrypt( transaction.concassage().encode() , 32 )
        return Transaction( self.clef_publique, destinataire, montant, signature[0].hex() )
    
def nouvel_utilisateur():
    clef = RSA.generate(1024)
    clef_publique = clef.exportKey()[31:-29].decode()
    clef_privée = clef.publickey().exportKey()[26:-24].decode()
    return Utilisateur(clef_privée, clef_publique)

def importer_clef_privée( clef ):
    clef = "-----BEGIN PUBLIC KEY-----" + clef + "-----END PUBLIC KEY-----"
    return RSA.importKey( clef.encode() )

def importer_clef_publique( clef ):
    clef = "-----BEGIN RSA PRIVATE KEY-----" + clef + "-----END RSA PRIVATE KEY-----"
    return RSA.importKey( clef.encode() )

    
    
#Tests

def nChain(*args):
    d = []
    for i in args:
        d += [Transaction("0", i.clef_publique, 1000, "KDO")]
    return Chaine_de_Blocs(Bloc(datetime.datetime.now(), d, -1, "Premier bloc"))

k=10
users = [ nouvel_utilisateur() for i in range(k) ]
chain = nChain(*users)
trans = [ users[3].envoyer(users[i+1].clef_publique, 10) for i in range(k//3)]
chain.ajout_de_block(trans)


none = "0"

while hash[1] != str(0) or  hash[0] != str(0) or hash[2] != str(0) :
    sha256 = hashlib.sha256()
    sha256.update(bytes(none, "utf-8"))
    hash = sha256.hexdigest()
    none +="0"
print(hash)
