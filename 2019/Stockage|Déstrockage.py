# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 08:58:16 2019

@author: Wakedel
"""

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
                "marquage": obj.marquage}
    
    # Si c'est une chaine de blocs.
    if isinstance(obj, Chaine_de_Blocs):
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
            bloc = Bloc( datetime.datetime.strptime( obj_dict["horodatage"],
                                                     "%Y-%m-%dT%H:%M:%S.%f"),
                         obj_dict["donnees"],
                         obj_dict["index"] - 1,
                         obj_dict["marquage_precedent"])
            bloc.nonce = obj_dict["nonce"]
            bloc.marquage = bloc.concassage()
            return bloc
        
        # Si c'est une chaine de blocs
        if obj_dict["__class__"] == "Bloc":
            return Chain( *obj_dict )
        
    #return objet



#Tests
with open("MaPlaylist.json", "w", encoding="utf-8") as fichier:
    json.dump(chain, fichier, indent=4, default=serialiseur_perso)

with open("MaPlaylist.json", "r", encoding="utf-8") as fichier:
    chaine = json.load(fichier, object_hook=deserialiseur_perso)
