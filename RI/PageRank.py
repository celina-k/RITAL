# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 09:29:53 2021

@author: GIANG Cécile, KHALFAT Célina
"""

##################### IMPORTATION DES LIBRAIRIES UTILES ######################

from collections import Counter
import numpy as np
import random as rd
from IRModel import *


############################# CLASSE PAGERANK ################################

class PageRank:
    """ Classe permettant d'introduire la notion de popularité des documents
        comme définis par l'algorithme PageRank.
        Attributs:
            * self.ref_index: IndexerSimple, référence de l'indexer
            * self.parser: Parser, référence du parser
            * self.model: IRModel, modèle à utiliser pour un premier ranking
                          sur nos documents
            * self.query: str, requête à traiter
            * self.n: int, nombre de Documents seeds à considérer, ie le nombre
                      de documents à prendre dans le ranking rendu par le modèle
            * self.k: int, nombre de Documents à choisir aléatoirement parmi
                      tous ceux pointant vers chaque Document
    """
    def __init__(self, ref_index, model, query, n, k):
        """ Constructeur de la classe PageRank.
        """
        self.ref_index = ref_index
        self.parser = ref_index.getParser()
        self.model = model
        self.query = query
        self.n = n
        self.k = k
        self.graph = self.buildGraph()
        self.mat = self.buildMat()
    
    def buildGraph(self):
        """ Construction du graphe pour le PageRank.
            On garde les n premiers noeuds du ranking retourné par le modèle, 
            puis on ajoute au graphe, pour chaque document D de seeds:
                * tous les documents cités par D
                * k documents qui citent D, choisis aléatoirement. Les répétitions
                  sont possibles si un document cite D à plusieurs reprises
        """
        # Initialisation du dictionnaire et de seeds
        graph = dict()
        seeds = list( self.model.getRanking( self.query ) )[ : self.n]
        
        for idDoc in seeds:
            
            # Traitement pour les documents cités par le document courant
            if idDoc not in graph.keys(): graph[idDoc] = []
            graph[idDoc] += self.parser.getHyperlinksFrom(idDoc)

            # On choisit k documents qui citent le Document courant (répétitions posssibles)
            linksTo = list( Counter( self.parser.getHyperlinksTo(idDoc) ).elements() )
            to_keep = rd.sample( linksTo , k = min( self.k, len(linksTo) ) )
            
            # Pour chacun d'entre eux, on rajoute le lien allant d'eux vers idDoc
            for id_from in to_keep:
                if id_from not in graph.keys(): graph[id_from] = []
                graph[id_from] += [idDoc]
                
        return graph
    
    def buildMat(self):
        """ Construction de la matrice de transitions P à partir de self.graph.
        """
        # Liste des noeuds sources et des noeuds destinations
        ifrom = set( [ k for k in self.graph.keys() ] )
        ito = set( [ v for all_values in self.graph.values() for v in all_values ] )
        
        self.inodes = sorted( list( ifrom.union(ito) ) )
        
        # Initialisation de la matrice
        P = np.zeros((len(self.inodes),len(self.inodes)))
        
        # Remplissage de la matrice
        for idDoc in self.graph.keys():
            # On retrouve l'indice de idDoc dans inodes
            i = self.inodes.index(idDoc)
            
            P[i] = np.array([ self.graph[self.inodes[i]].count(node) for node in self.inodes ])
            P[i] /= np.sum(P[i])
        
        return P
    
    def getScores(self, d = 0.8, eps = 1e-5, a = None, maxIter = 1000):
        """ Calcul des scores.
            @param d: float, damping factor (facteur d'amortissement)
            @param eps: float, écart maximum entre s au temps t et t + 1
            @param maxIter: int, nombre maximal d'itérations
            @param a: list(float), liste des probas a priori pour chaque noeud
            @return scores: (float) array, array des scores de chaque page
        """
        # Par défaut: la distribution initiale (a priori) est uniforme
        if a == None:
            a = np.array( [ 1 / len(self.mat) for i in range(len(self.mat)) ] )
            
        # Initialisation des scores
        scores_t0 = np.ones( len( self.mat ) , dtype=float )
        scores_t1 = np.ones( len( self.mat ) , dtype=float )  / len(scores_t0)
        diff_mean = 1
        
        # Compteur itérations
        iter = 0
        
        while ( diff_mean > eps and iter < maxIter ) :
            scores_t0 = np.copy( scores_t1 )
            scores_t1 = d * np.array([ np.sum( self.mat[ :, j ] * scores_t0 ) for j in range(len(self.mat)) ]) + ( 1 - d ) * a
            
            #Normalisation
            scores_t1 /= np.sum(scores_t1)
            
            # Critère de convergence
            diff_mean = np.mean( np.abs( scores_t1 - scores_t0 ) )
            iter += 1
        
        print('Convergence en', iter, ' itérations')
        
        # Scores sous la forme d'un dictionnaire trié (du plus pertinent au moins pertinent):
        scores = { self.inodes[i] : scores_t1[i] for i in range(len(self.inodes)) }
        
        return dict( sorted( scores.items(), reverse=True, key=lambda item: item[1] ) )

    def getGraph(self):
        return self.graph
    
    def getMat(self):
        return self.mat
    
    def getNodes(self):
        return self.inodes



##############################################################################

# parser = Parser('data\cacm\cacm.txt')
# i = IndexerSimple(parser)
# model = ModeleLangue(i)

# q = QueryParser('data/cacm/cacm.qry', 'data/cacm/cacm.rel')
# queries = q.getCollection()
# query = queries[57].getText()

# ------- Création de l'objet pagerank
# pr = PageRank(i, model, query, n = 30, k = 30)

# ------- Pour avoir le graphe
# pr.getGraph()

# ------- Pour avoir la matrice de transitions
# pr.getMat()

# ------- Pour avoir les scores de chaque noeud du graphe (trié)
# pr.getScores()