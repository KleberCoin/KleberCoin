# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 10:31:07 2019

"""

import hashlib

import datetime

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


def creation_premier_bloc():
    return Bloc(datetime.datetime.now(), "Premier bloc", -1, "Premier bloc")
        
class Chaine_de_Blocs:
    def __init__(self, premier_bloc):
        self.chain = [premier_bloc]
        
    def verification_de_chaine(): 
        return None

    # Traitement d'un nouveau bloc
    def verification_de_bloc(self, bloc):
        if bloc.marquage_précédent == self.chaine[-1].marquage:
            return True
        
    def verification_transactions(self, bloc):
        return True
        
    
    def ajout_de_block(self, bloc):
        if vérification_de_bloc(bloc) and vérification_transactions(bloc):
            self.chain.append(bloc)


class Transaction:
    def __init__(self, émetteur, destinataire, montant):
        
