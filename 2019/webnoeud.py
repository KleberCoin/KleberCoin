from flask import Flask
from flask import request
from flask import jsonify

import requests
import json

# Rappel : fonctionne avec chiffrement asymétrique: clé publique/clé privée. Seul l'auteur peut chiffrer ce qui va être déchiffrer par la clé publique

# POUR FAIRE UNE TRANSACTION : POST /transaction data:
#
#{
#  "de": "71238uqirbfh894-random-public-key-a-alkjdflakjfewn204ij",
#  "vers": "93j4ivnqiopvh43-random-public-key-b-qjrgvnoeirbnferinfo",
#  "montant": 3,
#  "chiffrement_prive_transaction": "ihgohighsghgomihirmgiqùeoieùoijgermoihergoiergjhoefiqqhsfklghermsklghqlmekrgnelkghnrgklhn" --> Si il est déchiffré par la clé publique et correspond : c'st bon
#} "chiffrement privé transaction" = ""
#

verbose = True
ip_du_noeud = "192.168.0.1"

# Ce noeud est il le premier du réseau ?
premier_noeud = True
# Stockage des noeuds pair. Si pas premier_noeud
liste_des_pairs = ["192.168.0.2"]




# Init. Flask
noeud = Flask(__name__)


# Init. Pair de la Blockchain
if not premier_noeud and liste_des_pairs:
    # Récupération de la liste des autres pairs
    req = requests.get('http://%s/pairs' % liste_des_pairs[0]) # JSON {"adresses": ["192.168.0.1", "192.168.0.3"]} avec l'adresse du premier pair dedans
    donnees = req.json() #json.loads(req) # donnees > dictionnaire
    liste_des_pairs = donnees["adresses"] # donnes["adresses"] > liste
# A test


# Stockage des transactions du noeud dans une liste avant de l'ajouter dans un bloc
transaction_noeud = []




# Savoir si le noeud est up
@noeud.route("/statut", methods=["GET"])
def statut():
    if(verbose):
           # On print ce qu'on a fait
           print("envoi statut OK à %s" % request.remote_addr)
    return jsonify({"statut": "OK"}), 200

# Donner la liste des pairs connus sur demande
@noeud.route("/pairs", methods=["GET"])
def donner_les_pairs():
    pairs_a_envoyer = liste_des_pairs + [ip_du_noeud]
    if(verbose):
           # On print ce qu'on a fait
           print("Envoi de la liste des pairs à %s" % request.remote_addr)
    return jsonify({"adresses": pairs_a_envoyer}), 200

# Ajout du pair nous envoyant une demande : test de son statut d'abord
@noeud.route("/ajout_pair", methods=["POST"])
def ajout_pair():
    statut_pair = requests.get('http://%s/statut' % request.remote_addr)
    statut_pair = statut_pair.json()
    if(statut_pair["statut"] == "OK"):
        liste_des_pairs.append(request.remote_addr)
        if(verbose):
               # On print ce qu'on a fait
               print("Ajout du pair %s" % request.remote_addr)
        return jsonify({"statut": "Fait"}), 200
    else:
        return jsonify({"statut": "Erreur"}), 400

# Envoie la version du noeud de la chaine
@noeud.route("/chaine", methods=["GET"])
def donner_la_chaine():
    # TODO: return la chaine de bloc
    if(verbose):
           # On print ce qu'on a fait
           print("Don de la chaine de bloc à %s" % request.remote_addr)
    return jsonify(chaine_de_bloc)

# Ecoute serveur web pour utilisateur veut faire une transaction
@noeud.route("/transaction", methods=["POST"])
def transaction():
    # Pour chaque requete on extrait les donnees de transaction
    nouv_transaction = request.get_json()

    # On vérifie que la transaction est authentique
    # TODO: vérifier la transaction
    if(transaction.verifie(nouv_transaction)):

        # On ajoute cette transaction à la liste
        transaction_noeud.append(nouv_transaction)
    	if(verbose):
               # On print que on a recu la transaction
               print("Nouvelle transaction")
               print("DE: {}".format(nouv_transaction["de"]))
               print("VERS: {}".format(nouv_transaction["vers"]))
               print("MONTANT: {}\n".format(nouv_transaction["montant"]))
        # On repond ok
        return 200
      else:
        return 400

def main():
    port = 13333
    if len(sys.argv) > 1:
        port = sys.argv[1]
    chaine_de_bloc.append(premier_bloc)
    node.run(port=port)

if __name__ == '__main__':
    main()
