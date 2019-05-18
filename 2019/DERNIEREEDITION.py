"""
Serveur web d'un noeud de la chaine de bloc KleberCoin

Launch : python noeud.py 110.87.12.66
                            /\
                        Ip du Noeud
"""
import sys
import json
import requests

from flask import Flask
from flask import request
from flask import jsonify

# TODO: Problème avec le sérialiseur
# SEPARER LE FICHIER EN MODULES
#from serialiseur import *
# from requetes import *


# Rappel : fonctionne avec chiffrement asymétrique: clé publique/clé privée.
#Seul l'auteur peut chiffrer ce qui va être déchiffrer par la clé publique


# PORT DES NOEUDS : 13333
global VERBOSE
VERBOSE = True
global IP_NOEUD
IP_NOEUD = sys.argv[1]

# Ce noeud est il le premier du réseau ?
global PREMIER_NOEUD
PREMIER_NOEUD = True


global liste_des_pairs
# Stockage des noeuds pair. Si pas PREMIER_NOEUD
liste_des_pairs = [] #["192.168.0.2"]

global chaine_de_blocs
chaine_de_blocs = "r"


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

def serialiseur_perso(obj):

    # Si c'est une transaction.
    if isinstance(obj, Transaction):
        return {"__class__": "Transaction",
                "emetteur": obj.émetteur,
                "destinataire": obj.destinataire,
                "montant": obj.montant,
                "signature": obj.signature}

    # Si c'est un bloc.
    if isinstance(obj, Block):
        return {"__class__": "Bloc",
                "index": obj.index,
                "horodatage": obj.horodatage.isoformat(),
                "donnees": obj.données,
                "marquage_precedent": obj.marquage_précédent,
                "nonce": obj.nonce,
                "marquage": obj.marquage}

    # Si c'est une chaine de blocs.
    if isinstance(obj, Blockchain):
        return {"__class__": "Chaine de Blocs",
                "chaine": obj.chaine}

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
            bloc = Block( obj_dict["donnees"],
                         obj_dict["index"] - 1,
                         obj_dict["marquage_precedent"],
                         date = datetime.datetime.strptime( obj_dict["horodatage"],
                                                     "%Y-%m-%dT%H:%M:%S.%f"))
            bloc.nonce = obj_dict["nonce"]
            bloc.marquage = bloc.hash()
            return bloc

        # Si c'est une chaine de blocs
        if obj_dict["__class__"] == "Chaine de Blocs":
            #del( obj_dict["__class__"] )
            return Blockchain( *obj_dict["chaine"] )

#return objet
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
    chaine_de_blocs = json.loads(req, object_hook=deserialiseur_perso)
    if(VERBOSE):
        print("Pris la chaine de {} ".format(ip_pair))
    return chaine_de_blocs


def se_montrer_pair(ip_pair):
    """ Montrer qu'on est un pair à un pair """
    try:
        req = requests.post('http://{}:13333/ajout_pair'.format(ip_pair))
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

    # On vérifie si il est pas déjà dans la liste
    if(request.remote_addr not in liste_des_pairs):
        liste_des_pairs.append(request.remote_addr)
        if(VERBOSE):
            print("Ajout du pair {}".format(request.remote_addr))
        return jsonify({"statut": "Fait"}), 200
    return jsonify({"statut": "Déjà fait"}), 200



@noeud.route("/chaine", methods=["GET"])
def donner_la_chaine():
    """ Envoie la version du noeud de la chaine """
    # TODO: bcp de tests
    global chaine_de_blocs
    if(VERBOSE):
        print("Don de la chaine de bloc à {}".format(request.remote_addr))
    return jsonify(json.dumps(chaine_de_blocs, indent=4,default=serialiseur_perso)),200


@noeud.route("/transaction", methods=["POST"])
def transaction():
    """ Ecoute serveur web pour utilisateur qui veut faire une transaction """
    # Pour chaque requete on extrait les donnees de transaction
    # TODO: vérifier que ca marche
    nouv_transaction = json.loads(request, object_hook=deserialiseur_perso)


    # On vérifie que la transaction est authentique
    # TODO: vérifier la transaction
    à_vérifier = { transaction.émetteur: -transaction.montant }
    invalides = []
    valides = []

    chaine_de_blocs.vérification_des_transactions(à_vérifier, valides, invalides, len(chaine_de_blocs))

    if valides:

        # On ajoute cette transaction à la liste
        transaction_noeud.append(nouv_transaction)
        # vu qu'on s'en balec de l'optimisation, on est pas pressé et on réplique la transaction à tous les noeuds
        #TODO: tester si ca marche ;; ca passe ou ca casse
        for pair in liste_des_pairs:
            try:
                req = requests.post('http://{}:13333/transaction'.format(ip_pair), data=request.get_json(), headers={'content-type': 'application/json'})
            except:
                if(VERBOSE):
                    print("Echec envoi transaction {} :(".format(ip_pair))

        if(VERBOSE):
            print("Nouvelle transaction")
            print("DE: {}".format(nouv_transaction["émetteur"]))
            print("VERS: {}".format(nouv_transaction["destinataire"]))
            print("MONTANT: {}\n".format(nouv_transaction["montant"]))
            print("SIGNATURE: {}\n".format(nouv_transaction["signature"]))
        # On repond ok
        return 200
    return 400






################################################################################
#################################### MAIN ######################################
################################################################################

def main():
    global chaine_de_blocs
    global liste_des_pairs
    global PREMIER_NOEUD



    #Si le premier bloc
    if PREMIER_NOEUD:
        chaine_de_blocs = Blockchain(Block("premier bloc", -1, "lakfjzrfoaheizrguzgv"))

    # On assume qu'un nouveau pair qui n'est pas le premier va aller
    # se présenter chez tous les pairs de la chaine de block, puis va
    # télécharger la plus longue chaine_de_blocs


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
        
    noeud.run(port=13333)


if __name__ == '__main__':
    main()
