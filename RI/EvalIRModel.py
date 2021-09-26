# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 09:29:53 2021

@author: GIANG Cécile, KHALFAT Célina
"""

##################### IMPORTATION DES LIBRAIRIES UTILES ####################

import numpy as np
import pandas as pd


############################ CLASSE EVALIRMODEL #############################

class EvalIRModel():
    """ Classe permettant d'évaluer différents modèles de recherche sur un
        ensemble de requêtes, selon différentes mesures d'évaluation.
        On résumera les résultats pour l'ensemble des requêtes considérées
        selon différentes mesures d'évaluation.
        Attributs:
            * self.queries: dict(int, Query), dictionnaire des requêtes
            * self.models: dict(str, IRModel), dictionnaire des modèles (clé: nom du modèle)
            * self.metrics: dict(str, Metrics), dictionnaire des métriques
                            d'évalutation.
    """
    def __init__(self, queries, models, metrics):
        """ Constructeur de la classe EvalIRModel.
        """
        self.queries = queries
        self.models = models
        self.metrics = metrics


    def evalQuery(self, idQry, mod_name, met_name):
        """ Renvoie le score d'évaluation du ranking calculé par la métrique met_name
            et le modèle mod_name sur UNE SEULE requête idQry.
        """
        ranking = [ * self.models[ mod_name ].getRanking( self.queries[ idQry ].getText() ) ]
        return self.metrics[ met_name ].evalQuery( ranking, self.queries[ idQry ] )

    def evalQueryAllParams(self, idQry):
        """ Renvoie le dictionnaire des scores d'évaluation pour la requête
            idQry sur tous les modèles de self.models et toutes les métriques
            de self.metrics.
        """
        return { metric : { model : self.evalQuery(idQry, model, metric) for model in self.models } for metric in self.metrics }

    def evalParams(self, mod_name, met_name):
        """ Renvoie la moyenne et l'écart-type des évaluations sur l'ensemble
            des requêtes pour un modèle mod_name et une mesure met_name.
        """
        evals = [ self.evalQuery(idQry, mod_name, met_name) for idQry in self.queries.keys() ]
        return np.mean( evals ), np.std( evals )

    def evalAllParams(self):
        """ Renvoie la moyenne et l'écart-type des évaluations sur l'ensemble
            des requêtes pour tout modèle de self.models et toute mesure
            de self.metrics.
        """
        return {metric : { model: self.evalParams(model, metric) for model in self.models } for metric in self.metrics }

    def statsDataFrame(self):
        stats = self.evalAllParams()
        return pd.DataFrame.from_dict( stats )

## Tests
# =============================================================================
#
# q = QueryParser('data/cisi/cisi.qry', 'data/cisi/cisi.rel')
#
# queries = q.getCollection()
# models = {'langue' : ModeleLangue(i), 'okapi' : Okapi(i)}
# metrics = {'precision' : Precision(), 'rappel' : Rappel(), 'fmesure' : FMesure(), 'avgp' : AvgP(), 'rr': RR(), 'dcg' : DCG(), 'ndcg' : NDCG()}
#
# eval_ir = EvalIRModel(queries, models, metrics)
# =============================================================================
