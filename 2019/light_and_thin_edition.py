# -*- coding: utf-8 -*-

import hashlib
from Crypto.PublicKey import RSA

import datetime

class Bloc:
    def __init__(self, date, données, index_précédent, marquage_précédent):
        self.index = index_précédent + 1
        self.horodatage = date
        self.données = données
        self.marquage_précédent = marquage_précédent
        self.marquage = self.concassage()
        
    def concassage(self):
        sha256 = hashlib.sha256()
        sha256.update(bytes(str(self.index),"utf-8") +
                        bytes(str(self.horodatage),"utf-8") +
                        bytes(str(self.données),"utf-8") +
                        bytes(str(self.marquage_précédent),"utf-8") +
                        bytes(str(self.cible),"utf-8"))
        return sha256.hexdigest()
    
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
        
    
    def ajout(self, *blocs):
        for bloc in blocs:
            if self.vérification_de_bloc(bloc):
                self.chaine.append(bloc)

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
 
def importer_clef_privée( clef ):
    clef = "-----BEGIN PUBLIC KEY-----" + clef + "-----END PUBLIC KEY-----"
    return RSA.importKey( clef.encode() )

def importer_clef_publique( clef ):
    clef = "-----BEGIN RSA PRIVATE KEY-----" + clef + "-----END RSA PRIVATE KEY-----"
    return RSA.importKey( clef.encode() )

def nouvel_utilisateur():
    clef = RSA.generate(1024)
    clef_publique = clef.exportKey()[31:-29].decode()
    clef_privée = clef.publickey().exportKey()[26:-24].decode()
    return Utilisateur(clef_privée, clef_publique)

def création_premier_bloc():
    return Bloc(datetime.datetime.now(), "Premier bloc", -1, "Premier bloc")
