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
liste_des_pairs = ["192.168.0.2"]



# Init. Flask
noeud = Flask(__name__)



# A test


# Stockage des transactions du noeud dans une liste avant de l'ajouter dans un
# bloc
transaction_noeud = []
################################################################################
############################## FONCTIONS NOEUD #################################
################################################################################

def prendre_statut(ip_pair):
    """ Prendre le statut d'un pair, savoir s'il est actif """
    statut_pair = requests.get('http://{}/statut:13333'.format(ip_pair))
    statut_pair = statut_pair.json()
    if(statut_pair["statut"] == "OK"):
        return True
    return False

def prendre_pairs_connus(ip_pair):
    """ Prendre la liste des pairs d'un pair """
    return True

def prendre_chaine(ip_pair):
    """ Prendre la chaine d'un pair """
    return True

def se_montrer_pair(ip_pair):
    """ Montrer qu'on est un pair à un pair """
    req = requests.get('http://{}/ajout_pair:13333'.format(ip_pair))
    if(req.status_code == 200):
        if(VERBOSE):
            print("Accepté comme pair chez {}".format(ip_pair))
        return True
    if(VERBOSE):
        print("Pas Accepté comme pair chez {}  :(".format(ip_pair))
    return False



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
    if(VERBOSE):
        print("Don de la chaine de bloc à {}".format(request.remote_addr))
    return jsonify(chaine_de_bloc)


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
    if(PREMIER_NOEUD):
        chaine_de_bloc.append(premier_bloc)
    noeud.run(port=13333)


    # On assume qu'un nouveau pair qui n'est pas le premier va aller
    # se présenter chez tous les pairs de la chaine de block, puis va
    # télécharger la plus longue chaine_de_bloc


    # Init. Pair de la Blockchain
    if not PREMIER_NOEUD and liste_des_pairs:
        # Récupération de la liste des autres pairs
        req = requests.get('http://{}/pairs:13333'.format(liste_des_pairs[0]))
        # JSON {"adresses": ["192.168.0.1", "192.168.0.3"]} avec
        # l'adresse du premier pair dedans
        donnees = req.json() #json.loads(req) # donnees > dictionnaire
        liste_des_pairs = donnees["adresses"] # donnes["adresses"] > liste

        # Présentation chez les autres pairs
        for pair in liste_des_pairs:
            se_montrer_pair(pair)


if __name__ == '__main__':
    main()
