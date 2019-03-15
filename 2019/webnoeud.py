"""
Serveur web d'un noeud de la chaine de bloc KleberCoin
"""

import json
import requests

from flask import Flask
from flask import request
from flask import jsonify


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
############################## A REMPLACER PAR UN MODULE #################################
################################################################################




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
############################## FONCTIONS NOEUD #################################
################################################################################



def prendre_statut(ip_pair):
    """ Prendre le statut d'un pair, savoir s'il est actif """
    statut_pair = requests.get('http://{}:13333/statut'.format(ip_pair)).content
    #statut_pair = statut_pair.json()
    statut_pair = json.loads(statut_pair)
    if(statut_pair["statut"] == "OK"):
        return True
    return False

def prendre_pairs_connus(ip_pair):
    """ Prendre la liste des pairs d'un pair """
    # Récupération de la liste des autres pairs
    req = requests.get('http://{}:13333/pairs'.format(ip_pair)).content
    # JSON {"adresses": ["192.168.0.1", "192.168.0.3"]} avec
    # l'adresse du premier pair dedans
    donnees = json.loads(req) # donnees > dictionnaire
    # donnes["adresses"] > liste
    return donnees["adresses"]

def prendre_chaine(ip_pair):
    """ Prendre la chaine d'un pair """
    req = requests.get('http://{}:13333/chaine'.format(ip_pair)).content
    # Conversion en dictionnaire python
    chaine_de_blocs = json.load(req, object_hook=deserialiseur)

    return chaine_de_blocs 


def se_montrer_pair(ip_pair):
    """ Montrer qu'on est un pair à un pair """
    req = requests.get('http://{}:13333/ajout_pair'.format(ip_pair))
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
    for ip_pair in liste_des_pairs:
        # prendre les chaines
        chaine = prendre_chaine(ip_pair);
        # Ajout à la liste
        chaines.append(chaine)
    return chaines

def plus_longue_chaine():
    global chaine_de_blocs
    chaine_longue = chaine_de_blocs
    for chaine in trouver_toutes_les_chaine():
        if len(chaine_longue) < len(chaine):
            chaine_longue = chaine
    return chaine_longue


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
    # TODO: return la chaine de bloc
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
