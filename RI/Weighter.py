# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 09:29:53 2021

@author: GIANG Cécile, KHALFAT Célina
"""

##################### IMPORTATION DES FICHIERS EXTERNES ####################

import textRepresenter as tr
from abc import ABC, abstractmethod
import math


############################## CLASSE WEIGHTER ##############################

class Weighter(ABC):
    """ Classe permettant de représenter les pondérations (poids) de Documents
        et de requêtes.
        Attributs:
            * self.ref_index: IndexerSimple, référence de l'indexer
            * self.index: dict(int, int), ensemble des index des Documents de la collection
            * self.index_inv: dict(str, int), ensemble des index des Documents de la collection
    """
    def __init__(self, ref_index):
        """ Constructeur de la classe Weighter.
            @param ref_index: IndexerSimple, référence de l'indexer
        """
        self.ref_index = ref_index
        self.index = ref_index.getIndex()
        self.index_inverse = ref_index.getIndexInverse()
    
    @abstractmethod
    def getWeightsForDoc(self, idDoc):
        """ Retourne les poids des termes pour un documents dont l'identifiant est idDoc.
        """
        pass
    
    @abstractmethod
    def getWeightsForStem(self, stem):
        """ Retourne les poids du terme stem pour tous les documents qui le contiennent.
        """
        pass
    
    @abstractmethod
    def getWeightsForQuery(self, query):
        """ Retourne les poids des termes de la requête query.
        """
        pass
    

############################## CLASSE WEIGHTER1 ##############################

class Weighter1(Weighter):
    """ Classe de pondération telle que:
            * w_td = tf_td et w_tq = 1 si t ∈ q
            * w_td = tf_td et w_tq = 0 sinon
    """
    def __init__(self, ref_index):
        super().__init__(ref_index)
    
    def getWeightsForDoc(self, idDoc):
        """ @param idDoc: int, identifiant du Document dans l'index
            @return w_td: dict(str, int), index du nombre d'occurrences par 
                          mot du Document
        """
        return self.ref_index.getTfsForDoc(idDoc)
    
    def getWeightsForStem(self, stem):
        """ @param stem: str, mot stemmisé
            @return w_td: dict(int, int), index inverse du nombre d'occurrences 
                          du terme stem dans la collection de Documents
        """
        return self.ref_index.getTfsForStem(stem)
    
    def getWeightsForQuery(self, query):
        """ @param query: str, requête
            @return w_tq: dict(str, 1), vaut 1 pour chaque terme de la quête
        """
        # Stemmisation de la requête
        ps = tr.PorterStemmer()
        query_index = ps.getTextRepresentation(query)
        
        return { word : 1 for word in query_index.keys() }
    

############################## CLASSE WEIGHTER2 ##############################

class Weighter2(Weighter):
    """ Classe de pondération telle que:
        * w_td = tf_td
        * w_tq = tf_tq
    """
    def __init__(self, ref_index):
        super().__init__(ref_index)
    
    def getWeightsForDoc(self, idDoc):
        """ @param idDoc: int, identifiant du Document dans l'index
            @return w_td: dict(str, int), index du nombre d'occurrences par 
                          mot du Document
        """
        return self.ref_index.getTfsForDoc(idDoc)
    
    def getWeightsForStem(self, stem):
        """ @param stem: str, mot stemmisé
            @return w_td: dict(int, int), index inverse du nombre d'occurrences 
                          du terme stem dans la collection de Documents
        """
        return self.ref_index.getTfsForStem(stem)
    
    def getWeightsForQuery(self, query):
        """ @param query: str, requête
            @return w_tq: dict(str, int), index du nombre d'occurrences
                          pour chaque terme de la requête
        """
        # Stemmisation de la requête
        ps = tr.PorterStemmer()
        return ps.getTextRepresentation(query)
    

############################## CLASSE WEIGHTER3 ##############################

class Weighter3(Weighter):
    """ Classe de pondération telle que:
            * w_td = tf_td et w_tq = idf_t si t ∈ q
            * w_td = tf_td et w_tq = 0 sinon
    """
    def __init__(self, ref_index):
        super().__init__(ref_index)
    
    def getWeightsForDoc(self, idDoc):
        """ @param idDoc: int, identifiant du Document dans l'index
            @return w_td: dict(str, int), index du nombre d'occurrences par 
                          mot du Document
        """
        return self.ref_index.getTfsForDoc(idDoc)
    
    def getWeightsForStem(self, stem):
        """ @param stem: str, mot stemmisé
            @return w_td: dict(int, int), index inverse du nombre d'occurrences 
                          du terme stem dans la collection de Documents
        """
        return self.ref_index.getTfsForStem(stem)
    
    def getWeightsForQuery(self, query):
        """ @param query: str, requête
            @return w_tq: dict(str, int), index du nombre d'occurrences
                          pour chaque terme de la requête
        """
        # Stemmisation de la requête
        ps = tr.PorterStemmer()
        query_index =  ps.getTextRepresentation(query)
        
        # Calcul de idf pour tous les mots de la requête qui sont dans la collection de Documents
        return {stem : self.ref_index.getIdf()[stem] for stem in query_index.keys() if stem in self.index_inverse.keys()}
        

############################## CLASSE WEIGHTER4 ##############################

class Weighter4(Weighter):
    """ Classe de pondération telle que:
            * w_td = 1 + log(tf_td) si t ∈ d, 0 sinon
            * w_tq = idf_t si t ∈ q, 0 sinon
    """
    def __init__(self, ref_index):
        super().__init__(ref_index)
    
    def getWeightsForDoc(self, idDoc):
        """ @param idDoc: int, identifiant du Document dans l'index
            @return w_td: dict(str, int), index de la pondération de chaque 
                          mot du Document
        """
        index_idDoc = self.ref_index.getTfsForDoc(idDoc)
        return { stem : 1 + math.log(tf) for stem, tf in index_idDoc.items()}
    
    def getWeightsForStem(self, stem):
        """ @param stem: str, mot stemmisé
            @return w_td: dict(int, int), index inverse de la pondération de
                          chaque terme stem dans la collection de Documents
        """
        index_inverse = self.ref_index.getTfsForStem(stem)
        return {idDoc : 1 + math.log(tf) for idDoc, tf in index_inverse.items()}
    
    def getWeightsForQuery(self, query):
        """ @param query: str, requête
            @return w_tq: dict(str, int), index du nombre d'occurrences
                          pour chaque terme de la requête
        """
        # Stemmisation de la requête
        ps = tr.PorterStemmer()
        query_index =  ps.getTextRepresentation(query)
        
        # Calcul de idf pour tous les mots de la requête
        return {stem : self.ref_index.getIdf()[stem] for stem in query_index.keys() if stem in self.index_inverse.keys()}
        

############################## CLASSE WEIGHTER5 ##############################

class Weighter5(Weighter):
    """ Classe de pondération telle que:
            * w_td = (1 + log(tf_td)) * idf_t si t ∈ d, 0 sinon
            * w_tq = (1 + log(tf_tq)) * idf_t si t ∈ q, 0 sinon
    """
    def __init__(self, ref_index):
        super().__init__(ref_index)
        self.idf = ref_index.getIdf()
    
    def getWeightsForDoc(self, idDoc):
        """ @param idDoc: int, identifiant du Document dans l'index
            @return w_td: dict(str, int), index de la pondération de chaque 
                          mot du Document
        """
        tf_idDoc = self.ref_index.getTfsForDoc(idDoc)
        idf_idDoc = {stem : self.idf[stem] for stem in tf_idDoc.keys()}
        
        return { stem : (1 + math.log(tf_idDoc[stem])) * idf_idDoc[stem] for stem, tf in tf_idDoc.items()}
    
    def getWeightsForStem(self, stem):
        """ @param stem: str, mot stemmisé
            @return w_td: dict(int, int), index inverse de la pondération de
                          chaque terme stem dans la collection de Documents
        """
        tf_stem = self.ref_index.getTfsForStem(stem)
        idf_stem = self.idf[stem]
        
        return { idDoc : (1 + math.log(tf_stem[idDoc])) * idf_stem for idDoc, tf in tf_stem.items()}
    
    def getWeightsForQuery(self, query):
        """ @param query: str, requête
            @return w_tq: dict(str, int), index de la pondération de chaque 
                          terme de la requête
        """
        # Stemmisation de la requête
        ps = tr.PorterStemmer()
        
        # Calcul des tf pour tous les mots de la requête
        query_tf =  ps.getTextRepresentation(query)
        
        # Calcul de idf pour tous les mots de la requête
        query_idf = {stem : self.ref_index.getIdf()[stem] for stem in query_tf.keys() if stem in self.index_inverse.keys() and self.ref_index.getIdf()[stem] != 0}
        
        return {stem : (1 + math.log(query_tf[stem])) * query_idf[stem] for stem in query_idf}