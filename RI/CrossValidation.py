# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 09:29:53 2021

@author: GIANG Cécile, KHALFAT Célina
"""

##################### IMPORTATION DES LIBRAIRIES UTILES ####################

import numpy as np
from IRModel import *
from Metrics import *
from EvalIRModel import *
from GridSearch import *


########################## CLASSE CROSSVALIDATION ############################

class CrossValidation:
    """ Classe permettant de trouver la combinaison de paramètres donnant la
        meilleure valeur de métrique pour un modèle.
            * self.queries: dict(int, Query), dictionnaire des requêtes
    """
    def __init__(self, ref_index, queries, k = 10):
        """ Constructeur de la classe GridSearch.
        """
        self.index = ref_index
        self.queries = queries  
        self.k = k
        self.metrics = {'precision' : Precision(), 'rappel' : Rappel(), 'fmesure' : FMesure(), 'avgp' : AvgP(), 'rr': RR(), 'dcg' : DCG(), 'ndcg' : NDCG()}
        self.split = self.splitQueries()
    
    def splitQueries(self):
        """ Partitionne la collection de requêtes en 2 ensembles (train-test).
            @param k: int, nombre de partitions (k-folds)
            @return split: list(dict(int, Query)), liste de k ensembles de requêtes
        """        
        # Mélange uniforme des requêtes
        idQueries = list( self.queries.keys() )
        np.random.shuffle( idQueries )
        
        # Liste de 10 ensembles d'indices
        isplit = np.array_split( idQueries, self.k )
        
        # Création d'une liste de requêtes split
        split = []
        
        for index in isplit:
            split.append({ i : self.queries[i] for i in index })
        
        return split
    
    def mergeQueries(self, split, itest):
        """ Tranforme la liste de dictionnaires de requêtes (split) en une seule
            collection de requêtes, en ignorant le dictionnaire d'indice i.
            @param split: list(dict(int, Query)), liste de k-1 ensembles de requêtes
            @param itest: int, indice du dictionnaire à ignorer
            @return train: dict(int, Query), fusion des dictionnaires de split
            @return test: dict(int, Query), dictionnaire ignoré
        """
        # Initialisation de train et test
        train = dict()
        test = split[ itest ]
        
        for i in range(len(split)):
            if i != itest: train = { **train, **split[i] }
        
        return train, test
    
    def getBestParams(self, model_name, metric_name, step=0.1):
        """ Cross validation pour trouver la combinaison de paramètres 
            optimisant la métrique pour le modèle donné.
            @param model_name: str, nom du modèle
            @param metric_name: str, nom de la métrique
            @param step: float, pas des paramètres
        """
        # Valeurs de métrique pour chaque fold test
        metValues = dict()
        
        # itest: indice du fold de test
        for itest in range(len(self.split)):
            
            # Génération des données d'apprentissage et de test
            train, test = self.mergeQueries( self.split, itest )
            
            # Appel à GridSearch
            gs = GridSearch( self.index , train, ratio = 1 )
            params = gs.getBestParams( model_name , metric_name )
            metValues[ params ] = gs.evalTest( test = test )
        
        if model_name=='langue':
            lambs = list( metValues.keys() )
            return np.mean( lambs )
        
        if model_name=='okapi':
            ks = [ k for k , b in metValues.keys() ]
            bs = [ b for k , b in metValues.keys() ]
            
            return np.mean( ks ) , np.mean( bs )