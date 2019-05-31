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


################################################################################
############################## CHAINE DE BLOCS #################################
################################################################################

import hashlib
from Crypto.PublicKey import RSA

import datetime

def sha256(*data):
    sha = hashlib.sha256()
    sha.update( bytes("".join([ str(inpu) for inpu in data ]), "utf-8") )
    return sha.hexdigest()

class Bloc:
    """
    Classe bloc
    """
    
    def __init__(self, données, index_précédent, marquage_précédent, cible=0 ,
                 date=datetime.datetime.now()):
        """
        Constructeur qui initialise les différentes variables contenues dans l'
        objet bloc
        """
        self.index = index_précédent + 1
        self.horodatage = date
        self.données = données
        self.marquage_précédent = marquage_précédent
        self.nonce = 0
        self.cible = cible # compris entre 0 et 255
        self.marquage = self.hash()
        
    def hash(self):
        """
        Méthode qui calcule l'empreinte (hash) du bloc par la fonction de 
        hachage sha 256
        """
        return sha256(self.index, 
                      self.horodatage,
                      self.données,
                      self.marquage_précédent,
                      self.nonce)
        
    """
    def nouveau(précédent, données): 
        return Bloc(données, précédent.index, précédent.marquage)
    """
    
    def suivant(self, données, cible):
        """
        Méthode qui facilite la création d'un nouveau bloc cohérent avec ce-dernier
        """
        return Bloc(données, self.index, self.marquage, cible=cible)
        
    def compte_0(self):
        """
        Méthode qui compte le nombre de 0 au début du hash du bloc (en binaire)
        pour permettre ensuite le minage
        """
        
        # On récupère le hash en binaire
        hash = bin(int(self.marquage, 16))[2:]
        
        # On procède au comptage
        i = 0
        while hash[i] == "0":
            i +=1
        return i


    def mine(self):
        """
        Méthode qui procède au minage
        """
        # Tant que le hash du bloc est en dehors de la cible
        while self.compte_0() < self.cible:
            # On modifie le nonce pour générer un autre hash pseudo-aléatoirement
            self.nonce += 1
            # On calcule le nouveau hash
            self.marquage = self.hash()
            
            
class Chaine_de_bloc:
    """
    Classe chaîne de bloc
    """
    
    def __init__(self, *premiers_blocs):
        self.chaine = [ *premiers_blocs ]
        self.cible = 0
        
    def __len__(self):
        """
        Méthode qui implémente la possibilité d'utiliser la fonction len() sur 
        l'objet chaine de bloc
        """
        return len( self.chaine )
    
    def nouveau_bloc(self, données):
        """
        Méthode qui facilite la création d'un nouveau bloc cohérent avec le 
        dernier de la chaine
        """
        return self.chaine[-1].suivant(données, self.cible)
        
    def vérification_de_chaine(self):
        """
        Méthode qui vérifie la validité de chaque bloc de la chaine en 
        commençant par le premier et renvoie en sortie une liste contenant 
        ceux invalides
        """
        
        invalides = []
        
        # On exclut le bloc initial (0) de la vérification puisque celui-ci
        # sera toujours vu comme invalide puisqu'il n'est précédé d'aucun autre
        for bloc in self.chaine[1:]:
            if not self.vérification_de_bloc(bloc):
                invalides += [bloc.index]
            
        return invalides

    def vérification_de_bloc(self, bloc):
        """
        Méthode qui vérifie la validité d'un bloc
        """
        
        # On vérifie d'abord s'il est cohérent avec le précédent dans la chaine
        if bloc.marquage_précédent != self.chaine[bloc.index - 1].marquage or \
            bloc.marquage != bloc.hash() or \
            bloc.index != 1 + self.chaine[ bloc.index - 1 ].index :
            print("Bloc %s invalide" % bloc.index)
            return False
        
        # On vérifie ensuite la validité des transactions qu'il contient
        à_vérifier = {}
        invalides = []
        valides = []
        
        # On inscrit dans le dictionnaire à_vérifier l'ensemble des demandes de
        # transferts de fonds en comptant le débit comme montant négatif
        for transaction in bloc.données:
            # On ne traite que les transaction signées
            if transaction.est_signée():
                if transaction.émetteur in à_vérifier:
                    à_vérifier[transaction.émetteur] += - transaction.montant
                else : à_vérifier[transaction.émetteur] = - transaction.montant
            else :
                invalides += [transaction.émetteur]
        
        # On applique ensuite la méthode vérification_des_transactions() à partir
        # du dernier bloc de la chaine avant celui que l'on vérifie
        n = (bloc.index - 1)
        self.vérification_des_transactions(à_vérifier, valides, invalides, n )
        
        #print("Valides : ", valides)
        #print("Invalides : ", invalides )
        
        # On exploite les résultats de la méthode précédente pour conclure de 
        # validité du bloc en question
        if len(invalides) == 0:
            # Si aucune transaction n'est invalide, le bloc est valide
            print("Bloc %s valide" % bloc.index)
            return True
        else : 
            # Sinon il ne l'est pas
            print("Bloc %s invalide" % bloc.index)
            return False
        
        
    def vérification_des_transactions(self, à_vérifier, valides, invalides, n):
        """
            Méthode récurrente qui trie les demandes de transferts de fonds 
            contenues dans le dictionnaire "à_vérifier" en ne considérant la 
            chaîne de blocs que jusqu'au bloc d'index n.
            Elle modifie la liste "valides" des émetteurs ayant les fonds
            nécessaires et la liste "invalides" des émetteurs ne les ayant
            pas.
        """
        
        # On itère toutes les transactions contenues dans le bloc d'indice n
        for transaction in self.chaine[n].données:
            # Si l'émetteur de la transaction est dans le dictionnaire, on 
            # compte le montant de celle-ci comme un débit
            if transaction.émetteur in à_vérifier:
                à_vérifier[transaction.émetteur] -= transaction.montant
            
            # Si le destinataire de la transaction est dans le dictionnaire, on 
            # compte le montant de celle-ci comme un crédit
            if transaction.destinataire in à_vérifier:
                à_vérifier[transaction.destinataire] += transaction.montant
            # Remarque : on utilise deux structures conditionnelles if pour le 
            # cas possible où un individu se transfèrerait des fonds à lui-même
                
        # On vérifie la situation de chaque compte à vérifier
        for key in list(à_vérifier):
            # Si le montant du compte est actuellement positif, il y a eu plus
            # de crédit que de débits donc on ajoute le compte dans la liste
            # validée et le supprime du dictionnaire à_vérifier
            if à_vérifier[key] >=0:
                del(à_vérifier[key])
                valides += [key]
                    
        # S'il reste des comptres à vérifier et qu'un bloc précédent existe,
        # on relance la même méthode sur le bloc précédent
        if len(list(à_vérifier)) !=0 and n > 0:
            self.vérification_des_transactions(à_vérifier, 
                                               valides, 
                                               invalides, 
                                               (n-1))
        # Dans le cas contraire, on conclut que les demandes de transaction des
        # comptes restants dans le dictionnaire à_vérifier étaient illégitimes
        else : invalides += list(à_vérifier)


    def solde(self, à_vérifier, m, n):
        """
        Méthode qui permet d'établir le solde pour des comptes du bloc m à n
        Cette fonction modifie un dictionnaire de la forme
            {"adresse du compte" : liquidité }
        en ajoutant à liquidité le solde entre les blocs d'indice m et n(inclus)
        """
        # On utilise un principe analogue à celui de la méthode 
        # vérification_des_transactions()
        for transaction in self.chaine[n].données:
            if transaction.émetteur in à_vérifier:
                à_vérifier[transaction.émetteur] -= transaction.montant
            if transaction.destinataire in à_vérifier:
                à_vérifier[transaction.destinataire] += transaction.montant
        if n > m : self.solde(à_vérifier, m, n-1)


    def ajout(self, bloc):
        """
        Méthode qui permet d'ajouter un bloc à la chaine
        """
        # On vérifie si le bloc est valide et si il se situe bien dans la cible
        if self.vérification_de_bloc(bloc) and \
            self.cible == bloc.compte_0():
            # Si oui on l'ajoute à la chaine
            self.chaine.append(bloc)
            return True
        else : return False
                
        # Si l'indice du bloc est un multiple de 14*24*60*6 (nombre de blocs 
        # voulus en 14 jours)
        if bloc.index % (14*24*60*6) == 0 :
            # On calul le décalage entre le nombre de jours prévus (14) et celui
            # constaté depuis le dernier bloc correspondant à ce critère
            décalage = 14 - (self.chaine[-1].date - self.chaine[bloc.index - 14*24*60*6].date).days
            # Si on est en avance, on augmente la difficulté de minage en 
            # augmentant la cible
            if décalage < -7:
                self.cible = self.chaine[-1].cible + 1
            # Si on est en retard, on diminue la difficulté de minage
            elif décalage > 7:
                self.cible = self.chaine[-1].cible - 1


class Transaction:
    """
    Classe transaction
    """
    def __init__(self, émetteur, destinataire, montant, signature):
        self.émetteur = émetteur
        self.destinataire = destinataire
        self.montant = montant
        self.signature = signature
    
    def hash(self):
        """
        Méthode qui calcule le hash de la transaction
        """
        return sha256(self.émetteur,
               self.destinataire,
               self.montant)
    
    def est_signée(self):
        """
        Vérifie si la transaction est signée
        """
        # On importe la clef publique qui accompagne la transaction
        clef = importer_clef_publique( self.émetteur )
        # On déchiffre la signature
        signature = clef.decrypt( bytes.fromhex( self.signature ) )
        # On vérifie si elle correspond bien au hash du bloc en question
        if signature.decode() == self.hash():
            return True
        else : return False
        

class User:
    """
    Classe utilisateur
    """
    def __init__(self, clef_privée, clef_publique):
        self.clef_privée = clef_privée
        self.clef_publique = clef_publique
        
    def envoyer(self, destinataire, montant):
        """
        Méthode permetant de signer une transaction
        """
        # On crée la transaction
        transaction = Transaction( self.clef_publique, destinataire, montant, "0" )
        # On importe la clef privée de l'utilisateur
        clef = importer_clef_privée(self.clef_privée)
        # On crée la signature à partir du hash de la transaction
        signature = clef.encrypt( transaction.hash().encode() , 32 )
        # On joint la signature à la transaction et on renvoie le tout
        return Transaction( self.clef_publique, destinataire, montant, signature[0].hex() )
    
    def nouveau():
        """
        Méthode permettant de créer facilement un nouvel utilisateur
        """
        clef = RSA.generate(1024)
        clef_publique = clef.exportKey()[31:-29].decode()
        clef_privée = clef.publickey().exportKey()[26:-24].decode()
        return User(clef_privée, clef_publique)
    
    
def importer_clef_privée( clef ):
    """
    Fonction qui facilite l'importation de clefs privées pour RSA
    """
    clef = "-----BEGIN PUBLIC KEY-----" + clef + "-----END PUBLIC KEY-----"
    return RSA.importKey( clef.encode() )

def importer_clef_publique( clef ):
    """
    Fonction qui facilite l'importation de clefs  publiques pour RSA
    """
    clef = "-----BEGIN RSA PRIVATE KEY-----" + clef + "-----END RSA PRIVATE KEY-----"
    return RSA.importKey( clef.encode() )


################################################################################
################################ Sérialiseur ###################################
################################################################################

import json

def serialiseur_perso(obj):

    # Si c'est une transaction.
    if isinstance(obj, Transaction):
        return {"__class__": "Transaction",
                "emetteur": obj.émetteur,
                "destinataire": obj.destinataire,
                "montant": obj.montant,
                "signature": obj.signature}

    # Si c'est un bloc.
    if isinstance(obj, Bloc):
        return {"__class__": "Bloc",
                "index": obj.index,
                "horodatage": obj.horodatage.isoformat(),
                "donnees": obj.données,
                "marquage_precedent": obj.marquage_précédent,
                "nonce": obj.nonce,
                "cible": obj.cible,
                "marquage": obj.marquage}
    
    # Si c'est une chaine de blocs.
    if isinstance(obj, Chaine_de_bloc):
        return {"__class__": "Chaine de Blocs",
                "chaine": obj.chaine,
                "cible": obj.cible}
    
    # Sinon le type de l'objet est inconnu, on lance une exception.
    raise TypeError(repr(obj) + " n'est pas sérialisable !")
    
    
    
def deserialiseur_perso(obj_dict):
    if "__class__" in obj_dict:
        
        # Si c'est une transaction
        if obj_dict["__class__"] == "Transaction":
            return Transaction( obj_dict["emetteur"],
                                obj_dict["destinataire"],
                                obj_dict["montant"],
                                obj_dict["signature"])
            
        # Si c'est un bloc
        if obj_dict["__class__"] == "Bloc":
            bloc = Bloc( obj_dict["donnees"],
                         obj_dict["index"] - 1,
                         obj_dict["marquage_precedent"],
                         cible = obj_dict["cible"] ,
                         date = datetime.datetime.strptime( obj_dict["horodatage"],
                                                     "%Y-%m-%dT%H:%M:%S.%f"))
            bloc.nonce = obj_dict["nonce"]
            bloc.marquage = obj_dict["marquage"]
            return bloc
        
        # Si c'est une chaine de blocs
        if obj_dict["__class__"] == "Chaine de Blocs":
            #del( obj_dict["__class__"] )
            chain = Chaine_de_bloc( *obj_dict["chaine"] )
            chain.cible = obj_dict["cible"]
            return chain
        
    return objet


################################################################################
########################## Tests de la blockchain ##############################
################################################################################
    
from random import randint #pour la génération de nombres entiers aléatoires

#on crée 12 utilisateurs
n = 12
users = [ User.nouveau() for i in range(n) ]
#on initialise le dictionnaire à_vérifier
à_vérifier = {}
for user in users:
    à_vérifier[user.clef_publique] = 0
#on crédite 10 des 12 comptes d'un montant de 100000
deus = User.nouveau()
trans0 = [  deus.envoyer(user.clef_publique , 100000) for user in users[:10] ]
#on initialise le premier bloc et la chaîne
bloc0 = Bloc(trans0, -1, "Premier")
chain = Chaine_de_bloc(bloc0)

#on crée 100 nouveaux blocs
for i in range(100):
    #on actualise le solde
    chain.solde(à_vérifier, i,i)
    
    #on affiche la liste des soldes
    soldes = [ à_vérifier[key] for key in list(à_vérifier) ]
    print(soldes)
    
    #on écrit des transactions
    trans = []
    for j in range( len(users) ):
        #choix du destinataire
        k = randint(1, n-1)
        destinataire = users[ (j + k) % n ].clef_publique
        #choix du montant
        montant = randint(0, à_vérifier[users[j].clef_publique])
        
        trans.append( users[j].envoyer( destinataire, montant ) )
    
    #on crée le nouveau bloc avec toutes nos transactions
    chain.ajout(chain.nouveau_bloc(trans))
    
print(soldes)

#on vérifier la validité de la chaine
chain.vérification_de_chaine()

#on retire la 3ème transaction du bloc 50
del chain.chaine[50].données[2]

#on vérifie si la chaine est toujours valide
chain.vérification_de_chaine()
