# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 09:29:53 2021

@author: GIANG Cécile, KHALFAT Célina
"""

##################### IMPORTATION DES FICHIERS EXTERNES ####################

import math
import textRepresenter as tr

########################### CLASSE INDEXERSIMPLE ###########################

class IndexerSimple:
    """ Classe permettant d'indexer une collection de documents rendue par la
        méthode getCollection() de la classe Parser. Génère les fichiers index
        correspondant à l'index et l'index inversé de la collection.
        Attributs:
            * self.collection: dict(int, Document), collection de Documents
            * self.index: dict(int, int), ensemble des index des Documents de la collection
            * self.index_inv: dict(str, int), ensemble des index des Documents de la collection
    """
    def __init__(self, parser):
        """ Constructeur de la classe IndexerSimple.
            @param parser: Parser, parser de la collection de documents
        """
        self.parser = parser
        self.collection = parser.getCollection()
        self.index = dict()
        self.index_inverse = dict()
        
        # Mise à jour de l'index et l'index inversé sur la collection
        self.indexation()
        self.idf = self.getIdf()
    
    def indexation(self):
        """ Calcule l'index et l'index inverse du document passé en paramètre.
            Le calcul des index se fera à partir du nombre d'occurrences de 
            chaque mot.
            Attention: l'index et l'index inversé sont des dictionnaires dont 
                       les clés sont l'identifiant du document, et non le 
                       numéro du document dans la collection
            @param document: Document, indice du document à parser dans la collection
            @return occurrences: dict(str, int), dictionnaire des occurrences
        """
        # Initialisation stemmer
        ps = tr.PorterStemmer()
        
        # Calcul de l'index et de l'index inversé
        
        for i in self.collection:
            
            # Récupération du texte du document
            document = self.collection[i]
            texte = document.getTexte()
            idDoc = document.getId()
            
            # Indexation du texte du document
            self.index[idDoc] = ps.getTextRepresentation(texte)
            
            # Calcul de l'index inverse
            for word in self.index[idDoc]:
                if word not in self.index_inverse: self.index_inverse[word] = dict()
                self.index_inverse[word][idDoc] = self.index[idDoc][word]
                
    
    # --------------- Calculs tf, idf, tf-idf ---------------
    
    def getTf(self, idDoc):
        """ Calcul des tf (nombre d'occurrences) pour chaque mot d'un document.
            @param idDoc: int, identifiant du document (balise .I)
            return tf: dict(str, int), nombre d'occurrences de chaque mot (tf)
        """
        return self.index[idDoc]
    
    def getDf(self):
        """ Renvoie pour chaque mot de la collection le nombre de documents
            dans lequel il apparaît.
            @return df: dict(str, int), pour chaque mot, nombre de documents
                        dans lequel il apparaît
        """
        # Initialisation du dictionnaire df
        df = dict()
        
        # Parcours de tous les documents
        for idDoc in self.index:
            for word in self.index[idDoc]:
                if word not in df:
                    df[word] = 1
                else:
                    df[word] += 1
        return df
        
    def getIdf(self):
        """ Renvoie pour chaque mot du document la valeur de son idf.
            @return idf: dict(str, float), pour chaque mot, son idf dans la collection
        """        
        # Calcul de df pour tous les mots de la collection
        df = self.getDf()
        # Calcul de idf pour tous les mots de la collection
        idf = {word : math.log((1 + len(self.collection)) / (1 + df[word])) for word in df}
        
        return idf
    
    def getTfIdf(self, idDoc):
        """ Calcule pour tous les mots d'un Document son tf-idf.
            @param idDoc: int, identifiant du Document dans la collection
            @return tf_idf: dict(str, float), pour chaque mot, son tf-idf
        """
        # Calcul de tf, self.idf est déjà un attribut de la classe IndexerSimple
        tf = self.getTf(idDoc)
        return {word : tf[word]*self.idf[word] for word in tf}
    
    
    # --------------- Getteurs représentations ---------------
    
    def getTfsForDoc(self, idDoc):
        """ Retourne la représentation (stem-tf) d’un document à partir de 
            l’index.
            Il s'agit en fait simplement du calcul des TF des mots du Document.
            @param idDoc: int, identifant du document (balise .I) dans la collection
        """
        return self.getTf(idDoc)
    
    def getTfIDFsForDoc(self, idDoc):
        """ Retourne la représentation (stem-TFIDF) d’un document à partir
            de l’index.
            Il s'agit en fait simplement du calcul des tf-idf des mots du Document.
            @param idDoc: int, identifant du document (balise .I) dans la collection
        """
        return self.getTfIdf(idDoc)
    
    def getTfsForStem(self, word):
        """ Retourne la représentation (doc-tf) d’un stem à partir de l’index
            inverse.
            Il s'agit en fait simplement du calcul du TF du mot word.
            @param word: str, stem de mot
        """
        return self.index_inverse[word]
    
    def getTfIDFsForStem(self, word):
        """ Retourne la représentation (doc-TFIDF) d’un stem à partir de
            l’index inverse.
            Il s'agit en fait simplement du calcul du tf-idf du mot word.
            @param word: str, stem de mot
        """
        return {idDoc : self.getTfIdf(idDoc)[word] for idDoc in self.index_inverse[word]}
    
    def getStrDoc(self, idDoc):
        """ Retourne la chaîne de caractère dont est issu un Document de la
            collection.
            @param: idDoc: int, identifiant du document (balise .I) dans 
                           la collection
        """
        for index, document in self.collection.items():
            if document.getId() == idDoc: return document.getTexte()[:-1]
    
    # ----------------- Getteurs attributs ------------------
    
    def getParser(self):
        return self.parser
    
    def getCollection(self):
        return self.collection
    
    def getIndex(self):
        return self.index
    
    def getIndexInverse(self):
        return self.index_inverse