# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 08:58:16 2019
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
            chain = Blockchain( *obj_dict["chaine"] )
            chain.cible = obj_dict["cible"]
            return chain
        
    #return objet
