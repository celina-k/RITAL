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


############################ CLASSE GRIDSEARCH #############################

class GridSearch:
    """ Classe permettant de trouver la combinaison de paramètres donnant la
        meilleure valeur de métrique pour un modèle.
            * self.queries: dict(int, Query), dictionnaire des requêtes
    """
    def __init__(self, ref_index, queries, ratio=0.7):
        """ Constructeur de la classe GridSearch.
        """
        self.index = ref_index
        self.queries = queries  
        self.ratio = ratio
        self.metrics = {'precision' : Precision(), 'rappel' : Rappel(), 'fmesure' : FMesure(), 'avgp' : AvgP(), 'rr': RR(), 'dcg' : DCG(), 'ndcg' : NDCG()}
        self.train, self.test = self.splitQueries()
        
    def splitQueries(self):
        """ Partitionne la collection de requêtes en 2 ensembles (train-test).
            @param ratio: float, ratio de requêtes pour la base d'apprentissage
            @return train: dict(int, Query), requêtes d'apprentissage
            @return test: dict(int, Query), requêtes d'évaluation
        """
        # Mélange uniforme des requêtes
        idQueries = list( self.queries.keys() )
        np.random.shuffle( idQueries )
        
        # Indice de séparation des données test-train
        isplit = int( len(idQueries) * self.ratio )
        
        # Création des ensembles train et test
        train = { i : self.queries[i] for i in idQueries[ : isplit ] }
        test = { i : self.queries[i] for i in idQueries[ isplit : ] }
        
        return train, test
    
    def getBestParams(self, model_name, metric_name, step=0.1):
        """ Trouve la combinaison de paramètres optimisant la métrique pour
            le modèle donné.
            @param model_name: str, nom du modèle
            @param metric_name: str, nom de la métrique
            @param step: float, pas des paramètres
        """
        # Nombre de valeurs prises par chaque paramètre
        bins = int(1/step) + 1
        
        # On garde en mémoire le modèle et la métrique utilisés
        self.model = model_name
        self.metric = metric_name
        
        if model_name=='langue':
            # Partition des paramètres, calcul des modèles pour chaque paramètre
            lambs = np.linspace(0, 1, bins)
            models = { l : ModeleLangue(self.index, lamb=l) for l in lambs }
            metrics = { metric_name : self.metrics[ metric_name ] }
            
            # Pour l'évaluation
            eir = EvalIRModel(self.train, models, metrics)
            evals = { model : eir.evalParams(model, metric_name)[0] for model in models }
            
            # On récupère le paramètre lambda optimal
            if metric_name=='rr':
                self.lamb = min(evals, key=lambda key: evals[key])
            else:
                self.lamb =  max(evals, key=lambda key: evals[key])
            
            return self.lamb
            
        if model_name=='okapi':
            # Partition des paramètres, calcul des modèles pour chaque combinaison de paramètres
            ks = np.linspace(0.7, 1.7, bins)
            bs = np.linspace(0, 1, bins)
            metrics = { metric_name : self.metrics[ metric_name ] }
            models = dict()
            
            # Calcul des modèles Okapi pour chaque combinaison (k,b)
            for k in ks:
                for b in bs:
                    models[(k,b)] = Okapi(self.index, k, b)
            
            # Pour l'évaluation
            eir = EvalIRModel(self.train, models, metrics)
            evals = dict()
            evals = { model : eir.evalParams(model, metric_name)[0] for model in models }
            
            # On récupère les paramètres k et b optimaux
            if metric_name=='rr':
                self.k, self.b = min(evals, key=lambda key: evals[key])
            else:
                self.k, self.b = max(evals, key=lambda key: evals[key])
            
            print(evals)
            input()
            
            return self.k, self.b
        
    def evalTest(self, test = None):
        """ Test des paramètres optimaux sur les requêtes d'évaluation.
        """
        if test == None: test = self.test
        
        if self.model == 'langue':
            eir = EvalIRModel(test, { self.model : ModeleLangue(self.index, self.lamb)}, { self.metric : self.metrics[ self.metric ] })
            return eir.evalParams(self.model, self.metric)[0]
        
        if self.model == 'okapi':
            eir = EvalIRModel(test, { self.model : Okapi(self.index, self.k, self.b)}, { self.metric : self.metrics[ self.metric ] })
            return eir.evalParams(self.model, self.metric)[0]