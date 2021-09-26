# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 09:29:53 2021

@author: GIANG Cécile, KHALFAT Célina
"""

##################### IMPORTATION DES LIBRAIRIES UTILES ####################

import numpy as np
from abc import ABC, abstractmethod


############################ CLASSE EVALMESURE #############################
 
class EvalMesure(ABC):
    """ Classe permettant d'évaluer le ranking des documents retournés par un
        modèle pour une requête donnée. Implémente les mesures de précision, 
        rappel, P@k, R@K, f-mesure, AvgP, MAP, MRR et NDCG.
    """
    def __init__(self):
        """ Constructeur de la classe EvalMesure.
        """
        pass
    
    @abstractmethod
    def evalQuery(self, ranking, query):
        """ Calcule la mesure pour la liste des documents retournés par un 
            modèle et un objet Query.
            @param ranking: list(int), liste des ids des documents pertinents,
                            classés par IRModel
            @param query: Query, requête
        """
        pass


############################# CLASSE PRECISION ###############################

class Precision(EvalMesure):
    """ Classe pour la mesure de précision à k (P@K).
    """
    def __init__(self, k = None):
        """ @param k: int, nombre de documents retenus dans le ranking
        """
        super().__init__()
        self.k = k
    
    def evalQuery(self, ranking, query):
        """ Evaluation du classement par mesure P@k
        """
        # Cas ranking vide
        if len(ranking) == 0: return 0.0
        
        # On ne garde que les self.k premiers documents du ranking
        if self.k == 0: return 0.0
        if self.k==None or self.k > len(ranking): self.k = len(ranking)
        
        # relDocs: liste des Documents pertinents pour la requête
        relDocs = [ *query.getRelDocs() ]
        if len(relDocs) == 0 : return 0.0
        
        return np.mean( [ 1 if ranking[i] in relDocs else 0 for i in range(self.k) ] )


############################### CLASSE RAPPEL ################################

class Rappel(EvalMesure):
    """ Classe pour la mesure de rappel à k (R@K).
    """
    def __init__(self, k = None):
        """ @param lim: int, nombre maximal de documents considérés dans le ranking
        """
        super().__init__()
        self.k = k
    
    def evalQuery(self, ranking, query):
        """ Evaluation du classement par mesure R@k
        """
        # Cas ranking vide
        if len(ranking) == 0: return 0.0
        # On ne garde que les self.k premiers documents du ranking
        if self.k == 0: return 0.0
        if self.k==None or self.k > len(ranking): self.k = len(ranking)
        
        # relDocs: liste des Documents pertinents pour la requête
        relDocs = [ *query.getRelDocs() ]
        if len(relDocs) == 0 : return 0.0
        
        return sum( [ 1 if ranking[i] in relDocs else 0 for i in range(self.k) ] ) / len(relDocs)


############################## CLASSE FMESURE ################################

class FMesure(EvalMesure):
    """ Classe pour la f-mesure, qui combine les deux métriques P@k et R@k.
    """
    def __init__(self, k = None, beta = 0.5):
        """ @param beta: float, paramètre qui donne plus d'importance au rappel
                         ou à la précision. Deux valeurs très fréquentes sont:
                        * beta = 2 pour donner plus de poids au rappel
                        * beta = 0.5 pour donner plus de poids à la précision
        """
        super().__init__()
        self.k = k
        self.beta = beta
    
    def evalQuery(self, ranking, query):
        """ Evaluation du classement par mesure F@k
        """
        # Cas ranking vide
        if len(ranking) == 0: return 0.0
        if len(query.getRelDocs()) == 0 : return 0.0
        
        p = Precision( self.k ).evalQuery( ranking, query )
        r = Rappel( self.k ).evalQuery( ranking, query )
        
        return ( 1 + self.beta**2 ) * ( p * r ) / ( self.beta**2 * p + r )


################################ CLASSE AVGP ################################

class AvgP(EvalMesure):
    """ Classe pour la mesure de précision moyenne AvgP.
    """
    def __init__(self):
        super().__init__()
    
    def evalQuery(self, ranking, query):
        """ Evaluation du classement par mesure AvgP
        """
        # Cas ranking vide
        if len(ranking) == 0: return 0.0
        
        # relDocs: liste des Documents pertinents pour la requête
        relDocs = [ *query.getRelDocs() ]
        if len(relDocs) == 0 : return 0.0
        
        return np.mean( [ Precision(k).evalQuery(ranking, query) for k in range( 1, len(ranking) + 1 ) if ranking[k-1] in relDocs ] )


################################# CLASSE RR #################################

class RR(EvalMesure):
    """ Classe pour la mesure du rang réciproque sur une requête, ie le rang
        du 1er document réellement pertinent dans ranking (RR: Reciprocal Rank)
    """
    def __init__(self):
        super().__init__()
    
    def evalQuery(self, ranking, query):
        """ Evaluation du classement par mesure RR
        """
        # Cas ranking vide
        if len(ranking) == 0: return -1
        
        # relDocs: liste des Documents pertinents pour la requête
        relDocs = [ *query.getRelDocs() ]
        if len(relDocs) == 0 : return -1
        
        truepos =  [1 if idDoc in relDocs else 0 for idDoc in ranking]
        
        if 1 in truepos:
            return truepos.index(1)
        else:
            return -1


################################ CLASSE DCG #################################

class DCG(EvalMesure):
    """ Classe pour la mesure DCG (gain d'information sur les p premiers docs)
        en fonction de leur position dans le ranking.
    """
    def __init__(self, p = None):
        super().__init__()
        self.p = p
    
    def evalQuery(self, ranking, query):
        """ Evaluation du classement par mesure DCG
        """
        # Cas ranking vide
        if len(ranking) == 0: return 0.0
        # On ne garde que les self.p premiers documents du ranking
        if self.p == 0: return 0.0
        if self.p==None or self.p > len(ranking): self.p = len(ranking)
        
        # relDocs: dictionnaire des Documents pertinents pour la requête et leur pertinence
        relDocs = { idDoc : relevance + 1 for idDoc, relevance in query.getRelDocs().items() }
        if len(relDocs) == 0 : return 0.0
        
        return sum( [ relDocs[ ranking[i] ] / np.log2( i + 2 ) for i in range(self.p) if ranking[i] in relDocs ] )
        

################################ CLASSE NDCG #################################

class NDCG(EvalMesure):
    """ Classe pour la mesure NDCG (version normalisée pour moyenner DCG sur
        un ensemble de requêtes).
    """
    def __init__(self, p = None):
        super().__init__()
        self.p = p
    
    def evalQuery(self, ranking, query):
        """ Evaluation du classement par mesure NDCG
        """
        # Cas ranking vide
        if len(ranking) == 0: return 0.0
        
        # iranking : ranking idéal (vide si aucun document pertinent n'est connu)
        iranking = [ * dict ( sorted( query.getRelDocs().items(), reverse=True, key=lambda item: item[1] ) ) ]
        if iranking == []: return 0.0
        
        if len(query.getRelDocs()) == 0 : return 0.0
        
        # Calcul DCG et IDCG
        dcg = DCG( self.p ).evalQuery( ranking, query )
        idcg = DCG( self.p ).evalQuery( iranking, query )
        
        return dcg / idcg


## Tests

# w5 = Weighter5(i)
# m = Vectoriel(i, w5, True)
# ranking = m.getRanking( qcoll[1].getText() )
# ranking = [*ranking]
# eq = PaK(10000)
# eq.evalQuery(ranking, qcoll[1])