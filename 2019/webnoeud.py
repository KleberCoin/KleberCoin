from flask import Flask
from flask import request


# Rappel : fonctionne avec chiffrement asymétrique: clé publique/clé privée. Seul l'auteur peut chiffrer ce qui va être déchiffrer par la clé publique

# POUR FAIRE UNE TRANSACTION : POST /transaction data:
/* 
{
  "de": "71238uqirbfh894-random-public-key-a-alkjdflakjfewn204ij",
  "vers": "93j4ivnqiopvh43-random-public-key-b-qjrgvnoeirbnferinfo",
  "montant": 3,
  "chiffrement_prive_transaction": "ihgohighsghgomihirmgiqùeoieùoijgermoihergoiergjhoefiqqhsfklghermsklghqlmekrgnelkghnrgklhn" --> Si il est déchiffré par la clé publique et correspond : c'st bon
} "chiffrement privé transaction" = ""
*/

verbose = True

# Init. Flask
noeud = Flask(__name__)

# Stockage des transactions du noeud dans une liste avant de l'ajouter dans un bloc
transaction_noeud = []

# Ecoute serveur web pour utilisateur veut faire une transaction
@noeud.route('/transaction', methods=['POST'])
def transaction():
  if(request.method == 'POST'):
  
    # Pour chaque requete on extrait les donnees de transaction
    nouv_transaction = request.get_json()
    
    # On vérifie que la transaction est authentique
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
        return "Transaction soumise avec succès"
    else:
        return "Erreur"

noeud.run(host='0.0.0.0', port=8912)
