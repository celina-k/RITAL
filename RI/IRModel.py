# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 09:29:53 2021

@author: GIANG Cécile, KHALFAT Célina
"""

##################### IMPORTATION DES LIBRAIRIES UTILES ####################

import textRepresenter as tr
import numpy as np


############################## CLASSE IRMODEL ##############################

class IRModel:
    """ Classe permettant de calculer la pertinence d'une collection de
        Documents à partir de l'index de la collection.
        Attributs:
            * self.ref_index: IndexerSimple, référence de l'indexer
            * self.index: dict(int, int), ensemble des index des Documents de la collection
            * self.index_inv: dict(str, int), ensemble des index des Documents de la collection
    """
    def __init__(self, ref_index):
        
        """ Constructeur de la classe IRModel.
            @param ref_index: IndexerSimple, référence de l'indexer
        """
        self.ref_index = ref_index
        self.index = ref_index.getIndex()
        self.index_inverse = ref_index.getIndexInverse()
        
    def getScores(query):
        """ Retourne les scores de chaque Document de la collection pour la 
            requête query.
        """
        pass
    
    def getRanking(self, query):
        """ @param query: str, requête
        """
        # Récupération des scores pour chaque Document de la collection
        # On ne gardera que les documents dont le score n'est pas nul
        scores = self.getScores(query)
        scores = { idDoc : weight for idDoc, weight in scores.items() if weight > 0}
        
        # Tri des documents par score décroissant
        return dict( sorted( scores.items(), reverse=True, key=lambda item: item[1] ) )
        
    
    
############################## CLASSE VECTORIEL ##############################

class Vectoriel(IRModel):
    """ Modèle vectoriel pour le classement de documents.
    """
    def __init__(self, ref_index, ref_weighters, normalized = False):
        """ Constructeur de la classe Vectoriel.
            @param ref_index: IndexerSimple, référence de l'indexer
            @param ref_weighter: Weighter, référence du weighter
            @param normalized: bool, si False: fonction de score scalaire, si
                               True: fonction de score cosinus
        """
        super().__init__(ref_index)
        self.weighters = ref_weighters
        self.normalized = normalized
        
        # Optimisation: on évite de calculer à chaque requête les normes des documents
        self.normsDocs = {idDoc : np.linalg.norm( list( self.weighters.getWeightsForDoc(idDoc).values())) for idDoc in self.index.keys()}
    
    def getScores(self, query):
        """ @param query: str, requête
        """
        # Poids de chaque terme de la requete
        query_w = self.weighters.getWeightsForQuery(query)
        # Norme de query
        normQ = np.linalg.norm( list( query_w.values() ) )
        
        scores = {idDoc : 0 for idDoc in self.index.keys()}
        
        # Calcul du produit scalaire
        for qstem in query_w.keys():
            stem_w = self.weighters.getWeightsForStem(qstem)
            for idDoc in stem_w.keys():
                scores[idDoc] += stem_w[idDoc] * query_w[qstem]
        
                # Cas score cosinus
                if self.normalized:
                    # Calcul du poids de chaque stem de query dans les Documents de la collection
                    scores[idDoc] /= np.sqrt(normQ) + np.sqrt(self.normsDocs[idDoc])
        
        return scores
    

############################ CLASSE MODELELANGUE ############################

class ModeleLangue(IRModel):
    """ Modèle langue pour le classement de documents (lissage Jelinek-Mercer).
    """
    def __init__(self, ref_index, lamb=0.8):
        """ Constructeur de la classe ModeleLangue.
            @param ref_index: IndexerSimple, référence de l'indexer
            @param lamb: float, lambda = 0.8 si requête courte, 0.2 sinon
        """
        super().__init__(ref_index)
        self.lamb = lamb
        # Nombre total d'occurrences (tout mot confondu) dans la collection
        self.tf_coll = sum( [ sum(list(self.index_inverse[stem].values())) for stem in self.index_inverse.keys() ] )
        # Calcul des longueurs de chaque document
        self.lenDocs = {idDoc : sum( list( self.index[idDoc].values() ) ) for idDoc in self.index.keys()}
        
    def getScores(self, query):
        """ @param query: str, requête
        """
        # Récupération des stems des termes de la requête
        ps = tr.PorterStemmer()
        query_index = ps.getTextRepresentation(query)

        # Initialisation des scores
        scores = {idDoc : 0 for idDoc in self.index.keys()}
        
        for qstem in query_index.keys():
            # Pour tout terme de la requête présent dans la collection
            if qstem in self.index_inverse.keys():
                # Calcul de p(t|Mc)
                tfs_qstem = self.index_inverse[qstem]
                pt_Mc = sum(tfs_qstem.values()) / self.tf_coll
                
                for idDoc in self.index.keys():
                    if scores[idDoc]==0: scores[idDoc] = 1
                    if idDoc in tfs_qstem.keys():
                        # Calcul de p(t|Md)
                        pt_Md = self.index_inverse[qstem][idDoc] / self.lenDocs[idDoc]
                        scores[idDoc] *= ( ( 1 - self.lamb ) * pt_Mc + self.lamb * pt_Md )
                    else:
                        scores[idDoc] *= ( 1 - self.lamb ) * pt_Mc
     
        return scores


############################ CLASSE OKAPI-BM25 ############################

class Okapi(IRModel):
    """ Modèle probabiliste Okapi-BM25 pour le classement de documents.
    """
    def __init__(self, ref_index, k=1.2, b=0.75):
        """ Constructeur de la classe Okapi.
            @param ref_index: IndexerSimple, référence de l'indexer
        """
        super().__init__(ref_index)
        self.k = k
        self.b = b
        # Calcul des longueurs de chaque document
        self.lenDocs = {idDoc : sum( list( self.index[idDoc].values() ) ) for idDoc in self.index.keys()}
        # Longueur moyenne des documents
        self.avgdl = np.mean( list( self.lenDocs.values() ) )
        # Récupération des idf pour la collection
        self.idf = self.ref_index.getIdf()
        
    def getScores(self, query):
        """ @param query: str, requête
        """
        # Récupération des stems des termes de la requête
        ps = tr.PorterStemmer()
        query_index = ps.getTextRepresentation(query)
        
        # Initialisation des scores
        scores = {idDoc : 0 for idDoc in self.index.keys()}
        
        for qstem in query_index.keys():
            if qstem in self.index_inverse.keys():
                
                # Récupération des tf de qstem pour chaque Document de la collection
                tfs = self.index_inverse[qstem]
                
                for idDoc in tfs.keys():
                    scores[idDoc] += ( self.idf[qstem] * tfs[idDoc] ) / ( tfs[idDoc] + self.k * ( 1 - self.b + self.b * self.lenDocs[idDoc]/self.avgdl ) )
                    
        return scores
    
# query = 'Une requête nekora assez banale store, ainsi qu\'une requête plus extraordinaire nekora'