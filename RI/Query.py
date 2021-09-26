# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 09:29:53 2021

@author: GIANG Cécile, KHALFAT Célina
"""

################# IMPORTATION REGEX: EXPRESSIONS REGULIERES #################

import re


################################ CLASSE QUERY ################################

class Query:
    """ Classe permettant de stocker, pour un fichier de requêtes, leur
        identifiant, leur texte ainsi que la liste des identifiants des 
        documents pertinents.
        Attributs:
            * self.id: int, identifiant de la requête
            * self.text: str, texte de la requête
            * self.relDocs: list(int), liste des identifiants des documents 
                            pertinents pour la requête
    """
    def __init__(self, data):
        """ Constructeur de la classe Query.
        """
        self.id = int(data['I'])
       
        if 'W' in data.keys(): self.text = data['W'][:-1]
        else: self.text = ''
        
        #self.relDocs = []
        self.relDocs = dict()
        
    def setText(self, text):
        """ Permet de rajouter à notre objet Query le texte de la requête.
            @param text: str, texte de la requête
        """
        self.text = text
    
    def addToRelDocs(self, idDoc, relvalue):
        """ Permet de rajouter un document à la liste des documents pertinents
            pour la requête.
            @param idDoc: int, identifiant d'une instance de Document
        """
        self.relDocs[idDoc] = relvalue
    
    # ----------------- Getteurs attributs -----------------
    
    def getId(self):
        return self.id
    
    def getText(self):
        return self.text
    
    def getRelDocs(self):
        return self.relDocs


########################### CLASSE QUERYPARSER ###########################

class QueryParser:
    """ Classe permettant de parser les fichier de requêtes (.qry) et de 
        jugement de pertinence (.rel), et en calcule la collection de Query.
    """
    def __init__(self, qryfile, relfile):
        """ Constructeur de la classe Query.
            @param qryfile: str, chemin vers le fichier de requêtes (.qry)
            @param relfile: str, chemin vers le fichier de pertinences (.rel)
        """
        self.collection = self.parse(qryfile, relfile)
    
    def parse(self, qryfile, relfile):
        """ Fonction créant le dictionnaire de Query associé à la collection
            de requêtes associée aux fichiers entrés en paramètres.
            @param qryfile: str, chemin vers le fichier de requêtes (.qry)
            @param relfile: str, chemin vers le fichier de pertinences (.rel)
        """
        # ----- Collection de Queries
        collection = dict()
        
        # ----- Ouverture du fichier de requêtes et récupération du contenu
        lines = open(qryfile, 'r').read().splitlines()
        dictionnaire = dict()
        
        # i: int, compteur de documents
        i = 0
        balise = ''
        for line in lines:
            if line == '':
                continue
            # Cas balise '.I'
            if(re.search('^[.]I', line)):
                i += 1
                balise = 'I'
                dictionnaire[i] = {'I' : int(line.split(' ')[-1])}
            else:
                if(re.search('^[.][A-Z]', line)):
                    balise = line[-1]
                    if balise == 'X':
                        dictionnaire[i]['X'] = []
                    else:
                        dictionnaire[i][balise] = ''
                else:
                    if balise == 'X':
                        dictionnaire[i][balise].append(line.split('\t'))
                    else:
                        dictionnaire[i][balise] += line + ' '
        
        # ----- Création de la collection de Queries correspondant
        for idQry, data in dictionnaire.items():
            collection[idQry] = Query(data)
        
        # ----- Ouverture du fichier de pertinences et récupération du contenu
        lines = open(relfile, 'r').read().splitlines()
        
        for line in lines:
            split = line.split()
            #collection[ int( split[0] ) ].addToRelDocs( int( split[1] ) )
            collection[ int( split[0] ) ].addToRelDocs( int( split[1] ) , float( split[3] ) )
        
        return collection
    
    def getCollection(self):
        return self.collection

## Test

# q = QueryParser('data/cacm/cacm.qry', 'data/cacm/cacm.rel')
# qcoll = q.getCollection()

#for query in qcoll.values():
#    print('' , query.getId(), ':', query.getRelDocs())