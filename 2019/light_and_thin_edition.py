# -*- coding: utf-8 -*-

import hashlib
from Crypto.PublicKey import RSA

import datetime

def sha256(*data):
    sha = hashlib.sha256()
    sha.update( bytes("".join([ str(inpu) for inpu in data ]), "utf-8") )
    return sha.hexdigest()

class Block:
    def __init__(self, données, index_précédent, marquage_précédent, date=datetime.datetime.now()):
        self.index = index_précédent + 1
        self.horodatage = date
        self.données = données
        self.marquage_précédent = marquage_précédent
        self.nonce = 0
        self.marquage = self.hash()
        
    def hash(self):
        hash_data = ""
        for data in self.données:
            if isinstance(data, Transaction):
                hash_data = sha256( hash_data + data.hash() + data.signature )
            else:
                hash_data = sha256( hash_data + str(data) )
        
        return sha256(self.index, 
                      self.horodatage,
                      hash_data,
                      self.marquage_précédent,
                      self.nonce)
    
    def new(précédent, données):
        return Bloc(données, précédent.index, précédent.marquage)
        
    
class Blockchain:
    def __init__(self, *premiers_blocs):
        self.chaine = [ *premiers_blocs ]
        
    def vérification_de_chaine(self):
        invalides = []
        for bloc in self.chaine:
            if not self.vérification_de_bloc(bloc):
                invalides += bloc.index
                
        return invalides

    # Traitement d'un nouveau bloc
    def vérification_de_bloc(self, bloc):
        if bloc.marquage_précédent != self.chaine[-1].marquage or \
            bloc.marquage != bloc.hash() or \
            bloc.index != 1 + self.chaine[-1].index :
            return False
        # C'est moche mais y'a plein d'autres choses à remettre entre
        else : return True
        
    
    def ajout(self, *blocs):
        for bloc in blocs:
            if self.vérification_de_bloc(bloc):
                self.chaine.append(bloc)

class Transaction:
    def __init__(self, émetteur, destinataire, montant, signature):
        self.émetteur = émetteur
        self.destinataire = destinataire
        self.montant = montant
        self.signature = signature
    
    def hash(self):
        return sha256(self.émetteur,
               self.destinataire,
               self.montant)
    
    def est_signée(self):
        clef = importer_clef_publique( self.émetteur )
        signature = clef.decrypt( bytes.fromhex( self.signature ) )
        if signature.decode() == self.hash():
            return True
        else : return False
        

class User:
    def __init__(self, clef_privée, clef_publique):
        self.clef_privée = clef_privée
        self.clef_publique = clef_publique
        
    def send(self, destinataire, montant):
        # à relier au réseau
        transaction = Transaction( self.clef_publique, destinataire, montant, "0" )
        clef = importer_clef_privée(self.clef_privée)
        signature = clef.encrypt( transaction.hash().encode() , 32 )
        return Transaction( self.clef_publique, destinataire, montant, signature[0].hex() )
    
    def new():
        clef = RSA.generate(1024)
        clef_publique = clef.exportKey()[31:-29].decode()
        clef_privée = clef.publickey().exportKey()[26:-24].decode()
        return User(clef_privée, clef_publique)
    
    
def importer_clef_privée( clef ):
    clef = "-----BEGIN PUBLIC KEY-----" + clef + "-----END PUBLIC KEY-----"
    return RSA.importKey( clef.encode() )

def importer_clef_publique( clef ):
    clef = "-----BEGIN RSA PRIVATE KEY-----" + clef + "-----END RSA PRIVATE KEY-----"
    return RSA.importKey( clef.encode() )
