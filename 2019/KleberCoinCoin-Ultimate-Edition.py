"""
Serveur web d'un noeud de la chaine de bloc KleberCoin
"""

import json
import requests

from flask import Flask
from flask import request
from flask import jsonify

# TODO: Problème avec le sérialiseur 
# TODO: SEPARER LE FICHIER EN MODULES 
#from serialiseur import *
# from requetes import * 


# Rappel : fonctionne avec chiffrement asymétrique: clé publique/clé privée.
#Seul l'auteur peut chiffrer ce qui va être déchiffrer par la clé publique

# POUR FAIRE UNE TRANSACTION : POST /transaction data:
#
#{
#  "de": "71238uqirbfh894-random-public-key-a-alkjdflakjfewn204ij",
#  "vers": "93j4ivnqiopvh43-random-public-key-b-qjrgvnoeirbnferinfo",
#  "montant": 3,
#  "chiffrement_prive_transaction": "ihgohighsghgomihirmgiqùeoieùoijgermoihergo
#iergjhoefiqqhsfklghermsklghqlmekrgnelkghnrgklhn" --> Si il est déchiffré par
#la clé publique et correspond : c'est bon
#} "chiffrement privé transaction" = ""
#
# PORT DES NOEUDS : 13333
global VERBOSE
VERBOSE = True
global IP_NOEUD
IP_NOEUD = "192.168.0.1"

# Ce noeud est il le premier du réseau ?
global PREMIER_NOEUD
PREMIER_NOEUD = True


global liste_des_pairs
# Stockage des noeuds pair. Si pas PREMIER_NOEUD
liste_des_pairs = [] #["192.168.0.2"]

global chaine_de_blocs
# TODO: intégrer avec le prog d'alex

# Init. Flask
noeud = Flask(__name__)



# A test


# Stockage des transactions du noeud dans une liste avant de l'ajouter dans un
# bloc
transaction_noeud = []
################################################################################
############################## CHAINE DE BLOCS #################################
################################################################################
################################################################################
############################## CHAINE DE BLOCS #################################
################################################################################
################################################################################
############################## CHAINE DE BLOCS #################################
################################################################################
################################################################################
############################## CHAINE DE BLOCS #################################
################################################################################

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




################################################################################
################################ SERIALISEUR ###################################
################################################################################
################################################################################
################################ SERIALISEUR ###################################
################################################################################
################################################################################
################################ SERIALISEUR ###################################
################################################################################
################################################################################
################################ SERIALISEUR ###################################
################################################################################
#TODO: a mettre à jour
def serialiseur(obj): 
    #Si c'est une transaction
    if isinstance(obj, Transaction):
        return {
            "__class__": "Transaction",
            "emetteur": obj.émetteur,
            "destinataire": obj.destinataire,
            "montant": obj.montant,
            "signature": obj.signature
        }
    
    # Si c'est un bloc
    if isinstance(obj, Bloc):
        return {
            "__class__": "Bloc",
            "index": obj.index,
            "horodatage": obj.horodatage.isoformat(),
            "donnees": obj.données,
            "marquage_precedent": obj.marquage_précédent,
            "nonce": obj.nonce,
            "marquage": obj.marquage
        }
        
    #Si c'est une chaine de blocs
    if isinstance(obj, Chaine_de_Blocs):
        return {
            "__class__": "Chaine de Blocs",
            "chaine": obj.chaine
        }
    
    #Sinon le type de l 'objet est inconnu, on lance une exception
    raise TypeError(repr(obj) + " n'est pas sérialisable !")
    
    
def deserialiseur(obj_dict):
        if "__class__" in obj_dict: 
            # Si c'est une transaction
            if obj_dict["__class__"] == "Transaction":
                return Transaction(obj_dict["emetteur"],
                    obj_dict["destinataire"],
                    obj_dict["montant"],
                    obj_dict["signature"])
            # Si c'est un bloc
            if obj_dict["__class__"] == "Bloc":
                bloc = Bloc(datetime.datetime.strptime(obj_dict["horodatage"],
                        "%Y-%m-%dT%H:%M:%S.%f"),
                    obj_dict["donnees"],
                    obj_dict["index"] - 1,
                    obj_dict["marquage_precedent"])
            bloc.nonce = obj_dict["nonce"]
            bloc.marquage = bloc.concassage()
            return bloc
            # Si c'est une chaine de blocs
            if obj_dict["__class__"] == "Bloc":
                return Chain( * obj_dict)


################################################################################
################################## REQUETES ####################################
################################################################################
################################################################################
################################## REQUETES ####################################
################################################################################
################################################################################
################################## REQUETES ####################################
################################################################################
################################################################################
################################## REQUETES ####################################
################################################################################
def prendre_statut(ip_pair):
    """ Prendre le statut d'un pair, savoir s'il est actif """
    try:
        statut_pair = requests.get('http://{}:13333/statut'.format(ip_pair)).content
    except:
        if(VERBOSE):
            print("Echec prise de statut de {}".format(ip_pair))
        return False
    #statut_pair = statut_pair.json()
    statut_pair = json.loads(statut_pair)
    if(statut_pair["statut"] == "OK"):
        if(VERBOSE):
            print("Pris le statut OK de {}".format(ip_pair))
        return True
    
    return False

def prendre_pairs_connus(ip_pair):
    """ Prendre la liste des pairs d'un pair """
    # Récupération de la liste des autres pairs
    try:
        req = requests.get('http://{}:13333/pairs'.format(ip_pair)).content
    except: 
        if(VERBOSE):
            print("Echec prise de pairs de {}  :(".format(ip_pair))
        return False
    # JSON {"adresses": ["192.168.0.1", "192.168.0.3"]} avec
    # l'adresse du premier pair dedans
    donnees = json.loads(req) # donnees > dictionnaire
    # donnes["adresses"] > liste
    if(VERBOSE):
        print("Pris les pairs de {} ".format(ip_pair))
    return donnees["adresses"]

def prendre_chaine(ip_pair):
    """ Prendre la chaine d'un pair """
    try:
        req = requests.get('http://{}:13333/chaine'.format(ip_pair)).content
    except:
        if(VERBOSE):
            print("Echec Prise de la chaine de {} :( ".format(ip_pair))
        return False
    
    # Conversion en dictionnaire python
    chaine_de_blocs = json.load(req, object_hook=deserialiseur)
    if(VERBOSE):
        print("Pris la chaine de {} ".format(ip_pair))
    return chaine_de_blocs 


def se_montrer_pair(ip_pair):
    """ Montrer qu'on est un pair à un pair """
    try:
        req = requests.get('http://{}:13333/ajout_pair'.format(ip_pair))
    except:
    if(VERBOSE):
        print("Echec se montrer pair chez {} :(".format(ip_pair))
        return False
    if(req.status_code == 200):
        if(VERBOSE):
            print("Accepté comme pair chez {}".format(ip_pair))
        return True
    if(VERBOSE):
        print("Pas Accepté comme pair chez {}  :(".format(ip_pair))
    return False

def trouver_toutes_les_chaine():
    # Prendre toutes les chaines des noeuds connus
    global liste_des_pairs
    chaines = []
    if(VERBOSE):
        print("Démarrage recherche de toutes les chaines")
    for ip_pair in liste_des_pairs:
        # prendre les chaines
        chaine = prendre_chaine(ip_pair);
        # Ajout à la liste
        chaines.append(chaine)
    return chaines

def plus_longue_chaine():
    # retourne la chaine la plus longue après avoir téléchargé toutes les chaines
    global chaine_de_blocs
    chaine_longue = chaine_de_blocs
    if(VERBOSE):
        print("Tri des chaines: recherche de la chaine la plus longue")
    for chaine in trouver_toutes_les_chaine():
        if len(chaine_longue) < len(chaine):
            chaine_longue = chaine
    return chaine_longue


################################################################################
################################ SERVEUR WEB ###################################
################################################################################
################################################################################
################################ SERVEUR WEB ###################################
################################################################################
################################################################################
################################ SERVEUR WEB ###################################
################################################################################
################################################################################
################################ SERVEUR WEB ###################################
################################################################################
@noeud.route("/statut", methods=["GET"])
def donner_statut():
    """ Retourne si le noeud est bien un noeud actif """
    if(VERBOSE):
        print("Envoi statut OK à {}".format(request.remote_addr))
    return jsonify({"statut": "OK"}), 200



@noeud.route("/pairs", methods=["GET"])
def donner_les_pairs():
    """ Donner la liste des pairs connus sur demande """
    pairs_a_envoyer = liste_des_pairs + [IP_NOEUD]
    if(VERBOSE):
        print("Envoi de la liste des pairs à {}".format(request.remote_addr))
    return jsonify({"adresses": pairs_a_envoyer}), 200


@noeud.route("/ajout_pair", methods=["POST"])
def ajout_pair():
    """ Ajout du pair nous envoyant une demande : test de son statut d'abord """

    # Test si le pair est réellement un pair
    if(prendre_statut(request.remote_addr)):
        # On vérifie si il est pas déjà dans la liste
        if(request.remote_addr not in liste_des_pairs):
            liste_des_pairs.append(request.remote_addr)
            if(VERBOSE):
                print("Ajout du pair {}".format(request.remote_addr))
            return jsonify({"statut": "Fait"}), 200
        return jsonify({"statut": "Déjà fait"}), 200
    return jsonify({"statut": "Erreur"}), 400


@noeud.route("/chaine", methods=["GET"])
def donner_la_chaine():
    """ Envoie la version du noeud de la chaine """
    # TODO: bcp de tests
    global chaine_de_blocs
    if(VERBOSE):
        print("Don de la chaine de bloc à {}".format(request.remote_addr))
    return jsonify(json.dump(chaine_de_blocs, indent=4,default=serialiseur)),200 # json.dump a tester


@noeud.route("/transaction", methods=["POST"])
def transaction():
    """ Ecoute serveur web pour utilisateur qui veut faire une transaction """
    # Pour chaque requete on extrait les donnees de transaction
    nouv_transaction = request.get_json()

    # On vérifie que la transaction est authentique
    # TODO: vérifier la transaction
    if(transaction.verifie(nouv_transaction)):

        # On ajoute cette transaction à la liste
        transaction_noeud.append(nouv_transaction)
        if(VERBOSE):
            print("Nouvelle transaction")
            print("DE: {}".format(nouv_transaction["de"]))
            print("VERS: {}".format(nouv_transaction["vers"]))
            print("MONTANT: {}\n".format(nouv_transaction["montant"]))
        # On repond ok
        return 200
    return 400






################################################################################
#################################### MAIN ######################################
################################################################################

def main():
    #if(PREMIER_NOEUD):
    #    chaine_de_bloc.append(premier_bloc)
    noeud.run(port=13333)


    # On assume qu'un nouveau pair qui n'est pas le premier va aller
    # se présenter chez tous les pairs de la chaine de block, puis va
    # télécharger la plus longue chaine_de_bloc


    # Init. Pair de la Blockchain
    if not PREMIER_NOEUD and liste_des_pairs:
        # Récupération de la liste des autres pairs

        liste_des_pairs = prendre_pairs_connus(liste_des_pairs[0])

        # Présentation chez les autres pairs
        for pair in liste_des_pairs:
            se_montrer_pair(pair)
        # Prendre toutes les chaines et choisir la plus grande
        chaine_de_blocs = plus_longue_chaine()
    elif not PREMIER_NOEUD and not liste_des_pairs:
        print("Erreur: Noeud pas le premier mais liste des pairs vide")

    print("noeud en ligne")

if __name__ == '__main__':
    main()
