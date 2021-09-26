# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 08:11:11 2021

@author: GIANG
"""

# Parser
parser = Parser('data\cacm\cacm.txt')
collection = parser.getCollection()

# Indexer
i = IndexerSimple(parser)
index = i.getIndex()
index_inverse = i.getIndexInverse()

# Query Parser
q = QueryParser('data/cacm/cacm.qry', 'data/cacm/cacm.rel')
queries = q.getCollection()
models = {'langue' : ModeleLangue(i), 'okapi' : Okapi(i)}
metrics = {'precision' : Precision(), 'rappel' : Rappel(), 'fmesure' : FMesure(), 'avgp' : AvgP(), 'rr': RR(), 'dcg' : DCG(), 'ndcg' : NDCG()}
eval_ir = EvalIRModel(queries, models, metrics)

