# -*- coding: utf-8 -*-
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
        self.marquage = self.concassage()
    
    def concassage(self):
        sha256 = hashlib.sha256()
        sha256.update(bytes(str(self.index),"utf-8") +
                        bytes(str(self.horodatage),"utf-8") +
                        bytes(str(self.données),"utf-8") +
                        bytes(str(self.marquage_précédent),"utf-8"))
        return sha256.hexdigest()


def création_premier_bloc():
    return Bloc(datetime.datetime.now(), "Premier bloc", -1, "Premier bloc")
        
class Chaine_de_Blocs:
    def __init__(self, premier_bloc):
        self.chaine = [premier_bloc]
        
    def vérification_de_chaine(): 
        return None

    # Traitement d'un nouveau bloc
    def vérification_de_bloc(self, bloc):
        if bloc.marquage_précédent != self.chaine[-1].marquage or \
            bloc.marquage != bloc.concassage() or \
            bloc.index != 1 + self.chaine[-1].index :
            return False
            
        à_vérifier = {}
    
        for transaction in bloc.données:
            if transaction.émetteur in à_vérifier:
                à_vérifier[transaction.émetteur] += - transaction.montant
            else : à_vérifier[transaction.émetteur] = - transaction.montant
        
        invalides = []
        valides = []
        
        n = (bloc.index - 1)
        self.vérification_des_transactions(à_vérifier, valides, invalides, n )
        
        print("Valides : ", valides)
        print("Invalides : ", invalides )
        
        if len(invalides) == 0:
            return True
        else : return False
        
            
    # Fonction qui trie les demandes de transfert de fonds contenues dans le
    # dictionnaire
    def vérification_des_transactions(self,à_vérifier, valides, invalides, n):
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


class Transaction:
    def __init__(self, émetteur, destinataire, montant, signature):
        self.émetteur = émetteur
        self.destinataire = destinataire
        self.montant = montant
        self.signature = signature
    
    def est_signée(self):
        clef = RSA.importKey(émetteur)
        signature = clef.decrypt(self.signature)
        if signature.decode() == self.destinataire + self.montant:
            return True
        else : return False
        

class Utilisateur:
    def __init__(self, clef_privée, clef_publique):
        self.clef_privée = clef_privée
        self.clef_publique = clef_publique
        
    def envoyer(self, destinataire, montant):
        # à relier au réseau
        clef = RSA.importKey(self.clef_privée)
        signature = clef.encrypt(destinataire + bytes( str(montant) , "utf-8") , 32)
        return Transaction(self.clef_publique, destinataire, montant, signature[0])
    
def nouvel_utilisateur():
    clef = RSA.generate(1024)
    clef_privée = clef.exportKey()
    clef_publique = clef.publickey().exportKey()
    return Utilisateur(clef_privée, clef_publique)

###############################################################################
"""
clef c'est la clef renvoyer [32:-30]
il faut ajouter -----BEGIN RSA PRIVATE KEY-----\n au début et \n-----END RSA PRIVATE KEY----- 
à la fin pour la remettre au bon format
"""

#Tests

def nChain(*args):
    d = []
    for i in args:
        d += [Transaction("0", i.clef_publique, 1000, "KDO")]
    return Chaine_de_Blocs(Bloc(datetime.datetime.now(), d, -1, "Premier bloc"))

k=10
users = [ nouvel_utilisateur() for i in range(k) ]
chain = nChain(*users)
trans = [ users[3].envoyer(users[i+1].clef_publique, 1000) for i in range(k//3)]
chain.ajout_de_block(trans)
