# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 09:29:53 2021

@author: GIANG Cécile, KHALFAT Célina
"""

#################### IMPORTATION DES FICHIERS EXTERNES ####################

import Parser as parser
import Indexer as indexer
import Query as query
import IRModel as model
import Metrics as metric
import EvalIRModel as evm
import PageRank as pagerank


######################### FICHIER DE TESTS DU CODE #########################

# ----------------------- Test parsing et indexation -----------------------

## 1- Tests sur le fichier `cacm.txt`

print('*** Parsing du fichier `cacm.txt` en cours ... ***')
p = parser.Parser('data/cacm/cacm.txt')            # parsing
print('*** Indexation en cours ... ***')
i = indexer.IndexerSimple(p)  # indexation

# Affichage de l'index et de l'index inversé du document d'identifiant 4204
input('\nLes TFs du document 4204 de `cacm.txt`, presser \'Entrée\':\n')
print(i.getTfsForDoc(4204))
input('\n\nLes TF-IDFs du document 4204 de `cacm.txt`, presser \'Entrée\':\n')
print(i.getTfIDFsForDoc(4204))
input('\n\nLes TFs du stem \'nekora\' dans `cacm.txt`, presser \'Entrée\':\n')
print(i.getTfsForStem('nekora'))
input('\n\nLes TF-IDFs du stem \'nekora\' dans `cacm.txt`, presser \'Entrée\':\n')
print(i.getTfIDFsForStem('nekora'))

# Affichage du texte du document d'identifiant 4203
input('\n\nTexte du document d\'identifiant 4023 dans `cacm.txt`, presser \'Entrée\':\n')
print(i.getStrDoc(4204))


# ------------------------------ Test requêtes ------------------------------

print('\n\n*** Lecture des requêtes en cours ... ***')
qp = query.QueryParser('data/cacm/cacm.qry', 'data/cacm/cacm.rel')

input('\n20e requête de `cacm.qry`, presser \'Entrée\':\n')
queries = qp.getCollection()
print(queries[20].text)


# ------------------------------- Test modèles ------------------------------

print('\n\n*** Création d\'un modèle de langue et d\'un modèle Okapi en cours ... ***')
models = {'langue' : model.ModeleLangue(i), 'okapi' : model.Okapi(i)}

m = models['okapi']
ranking_okapi = m.getRanking( queries[1].getText() )
ranking_okapi = [*ranking_okapi]
input('\n10 documents les plus pertinents selon le modèle Okapi pour la 1ère requête, presser \'Entrée\':\n')
print(ranking_okapi[:10])

m = models['langue']
ranking_langue = m.getRanking( queries[1].getText() )
ranking_langue = [*ranking_langue]
input('\n\n10 documents les plus pertinents selon le modèle de langue pour la 1ère requête, presser \'Entrée\':\n')
print(ranking_langue[:10])


# ------------------------------ Test métriques -----------------------------

print('\n\n*** Création des mesures en cours ... ***')
metrics = {'precision' : metric.Precision(), 'rappel' : metric.Rappel(), 'fmesure' : metric.FMesure(), 'avgp' : metric.AvgP(), 'rr': metric.RR(), 'dcg' : metric.DCG(), 'ndcg' : metric.NDCG()}

input('\n\nCalcul des mesures RR et NDCG pour le ranking rendu par okapi, presser \'Entrée\':\n')
print('Reciprocal Rank:', metric.RR().evalQuery(ranking_okapi, queries[1]))
print('NDCG:', metric.NDCG(p=10000).evalQuery(ranking_okapi, queries[1]))

input('\n\nCalcul des mesures RR et NDCG pour le ranking rendu par langue, presser \'Entrée\':\n')
print('Reciprocal Rank:', metric.RR().evalQuery(ranking_langue, queries[1]))
print('NDCG:', metric.NDCG(p=10000).evalQuery(ranking_langue, queries[1]))


# ----------------------------- Test évaluations ----------------------------

print('\n\n*** Evaluation de modèles sur toutes les requêtes avec la classe EvalIRModel des mesures en cours ... ***')
eval_ir = evm.EvalIRModel(queries, models, metrics)

input('\n\nRang moyen du premier document pertinent sur l\'ensemble des requêtes:\n')
print('\nOkapi:', eval_ir.evalParams(mod_name='okapi', met_name='rr'))
print('\nLangue:', eval_ir.evalParams(mod_name='langue', met_name='rr'))


# ------------------------------ Test PageRank ------------------------------

print('\n\n*** Création d\'une instance de PageRank en cours ... ***')

input('\n\nPageRank pour Okapi sur la 1ère requête, presser \'Entrée\':\n')
pr = pagerank.PageRank(i, models['okapi'], queries[1].text, n = 30, k = 30)
input('\n\nGraphe de transitions, presser \'Entrée\':\n')
network = pr.getGraph()
print(network)
input('\n\nMatrice de transitions, presser \'Entrée\':\n')
matrans = pr.getMat()
print(matrans)
input('\n\nScore du PageRank pour Okapi sur la 1ère requête, presser \'Entrée\':\n')
print(pr.getScores())


input('\n\nPageRank pour Langue sur la 1ère requête, presser \'Entrée\':\n')
pr = pagerank.PageRank(i, models['langue'], queries[1].text, n = 30, k = 30)
input('\n\nGraphe de transitions, presser \'Entrée\':\n')
network = pr.getGraph()
print(network)
input('\n\nMatrice de transitions, presser \'Entrée\':\n')
matrans = pr.getMat()
print(matrans)
input('\n\nScore du PageRank pour Langue sur la 1ère requête, presser \'Entrée\':\n')
print(pr.getScores())