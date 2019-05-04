# -*- coding: utf-8 -*-

#TO do : fixer un nombre de transactions par bloc pour ne pas inciter à en mettre 0 (moins à calculer pour les hashs) et baiser le système
"""
avec max : 

pour synchro : les noeuds peuvent s'échanger le hash de la totalité des trans en att pour se synchro après
    
    
listes globales:
    totalité transac
    transactions attente de vérif
    transactions vérifiées
    
penser à l'interface utilisateur:
    ouverture automatique de l'user à partir d'un .json
    variables : crédit (qui doit être mis à jour en temps réel)
    fonctions : envoyer demander vérification avant d'envoyer
       
"""

import hashlib
from Crypto.PublicKey import RSA

import datetime

def sha256(*data):
    sha = hashlib.sha256()
    sha.update( bytes("".join([ str(inpu) for inpu in data ]), "utf-8") )
    return sha.hexdigest()

class Block:
    def __init__(self, données, index_précédent, marquage_précédent, cible=0 ,date=datetime.datetime.now()):
        self.index = index_précédent + 1
        self.horodatage = date
        self.données = données
        self.marquage_précédent = marquage_précédent
        self.nonce = 0
        self.cible = cible  # entre 0 et 255 ou 256 ? |mettre dans le sérialiseur
        self.marquage = self.hash()
        
    def hash(self):
        """ useless comme y'aura pas d'erreurs
        hash_data = ""
        for data in self.données:
            if isinstance(data, Transaction):
                hash_data = sha256( hash_data + data.hash() + data.signature )
            else:
                raise TypeError("Le bloc ne peut contenir que des transactions)
            """
        return sha256(self.index, 
                      self.horodatage,
                      self.données,
                      self.marquage_précédent,
                      self.nonce)
    """
    def new(précédent, données): 
        return Bloc(données, précédent.index, précédent.marquage)
    """
    
    def next(self, données, cible): 
        return Block(données, self.index, self.marquage, cible=cible)
        
    def compte_0(self):
        # On récupère le hash en binaire
        hash = bin(int(self.marquage, 16))[2:]
        
        i = 0
        while hash[i] == "0":
            i +=1
        return i
    
    def mine(self):
        
        while self.compte_0() < self.cible:
            self.nonce += 1
            self.marquage = self.hash()
            
            
class Blockchain:
    def __init__(self, *premiers_blocs):
        self.chaine = [ *premiers_blocs ]
        self.cible = 0
        
    def __len__(self):
        return len( self.chaine )
    
    def new_block(self, données):
        return self.chaine[-1].next(données, self.cible)
        
    def vérification_de_chaine(self):
        invalides = []
        for bloc in self.chaine:
            if not self.vérification_de_bloc(bloc):
                invalides += [bloc.index]
                
        return invalides

    # Traitement d'un nouveau bloc
    def vérification_de_bloc(self, bloc):
        if bloc.marquage_précédent != self.chaine[bloc.index - 1].marquage or \
            bloc.marquage != bloc.hash() or \
            bloc.index != 1 + self.chaine[ bloc.index - 1 ].index :
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
            print("Bloc %s valide" % bloc.index)
            return True
        else : 
            print("Bloc %s invalide" % bloc.index)
            return False
        
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
            if transaction.destinataire in à_vérifier:
                    à_vérifier[transaction.destinataire] += transaction.montant
                    if à_vérifier[transaction.destinataire] >= 0:
                        del(à_vérifier[transaction.destinataire])
                        valides += [transaction.destinataire]
                    
        if len(list(à_vérifier)) !=0 and n > 1:
            self.vérification_des_transactions(à_vérifier, valides, invalides, (n-1))
        else : invalides += list(à_vérifier)
        
    
    def ajout(self, bloc):
        if self.vérification_de_bloc(bloc) and \
            self.cible == bloc.compte_0():
            self.chaine.append(bloc)
            return True
        else : return False
                
        if bloc.index % (14*24*60*6) == 0 :   #à changer peut être
            décalage = 14 - (self.chaine[-1].date - self.chaine[bloc.index - 14*24*60*6].date).days
            if décalage < -7:
                self.cible = self.chaine[-1].cible - 1
            elif décalage > 7:
                self.cible = self.chaine[-1].cible - 1


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
