# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 09:29:53 2021

@author: GIANG Cécile, KHALFAT Célina
"""

################# IMPORTATION REGEX: EXPRESSIONS REGULIERES #################

import re
import numpy as np

############################## CLASSE DOCUMENT ##############################

class Document:
    """ Classe permettant de stocker les documents contenus dans un fichier.
        Permet de stocker les différentes métadonnées, et d'accéder en particulier
        aux valeurs de l'identifiant et du texte.
        
        Nous considérerons que le constructeur prend en argument un dictionnaire
        ayant pour clés les différentes balises et pour valeur leur contenu.
        
        Balises:
            * .I: identifiant du document (OBLIGATOIRE)
            * .T: titre du document
            * .B: date de publication du document
            * .A: auteur du document
            * .K: mots-clés du document
            * .W: texte du document
            * .X: liens du document du document
    """
    def __init__(self, data):
        """ Construteur de la classe Document.
            @param data: dict(str, object), dictionnaire des métadonnées du document
        """
        self.id = int(data['I'])
        if 'T' in data.keys(): self.titre = data['T'][:-1]
        else: self.titre = ''
        if 'B' in data.keys(): self.date = data['B'][:-1]
        else: self.date = ''
        if 'A' in data.keys(): self.auteur = data['A'][:-1]
        else: self.auteur = ''
        if 'K' in data.keys(): self.mc = data['K'][:-1]
        else: self.mc = ''
        if 'W' in data.keys(): self.texte = data['W'][:-1]
        else: self.texte = ''
        if 'X' in data.keys(): self.liens = [ int( lien[0] ) for lien in data['X'] ]
        else: self.liens = None
        
    
    # ----------------- Getteurs attributs ------------------
    
    def getId(self):
        return self.id
    
    def getTitre(self):
        return self.titre
    
    def getDate(self):
        return self.date
    
    def getAuteur(self):
        return self.auteur
    
    def getMC(self):
        return self.mc
    
    def getTexte(self):
        return self.texte
    
    def getLiens(self):
        return self.liens


############################## CLASSE PARSER ##############################

class Parser:
    """ Classe permettant de parser la collection de documents (fichier .txt) 
        entrée en paramètre, en stockant les documents qu'elle contient dans 
        un dictionnaire de Documents.
    """
    def __init__(self, filename):
        """ Constructeur de la classe Parser.
            @param filename: str, nom du fichier .txt qui est la collection de
                             documents à parser.
        """
        self.collection = self.parse(filename)
        
        # Liste des documents cités par chaque document
        self.index_linksFrom = { self.collection[i].getId() : self.collection[i].getLiens() for i in self.collection }
        
        # Liste des documents qui citent chaque document
        self.index_linksTo = { self.collection[i].getId() : {} for i in self.collection }
        
        for i in self.collection:
            liens = self.collection[i].getLiens()
            if liens != None:
                for j in liens:
                    if i not in self.index_linksTo[j] : self.index_linksTo[j][i] = 0
                    self.index_linksTo[j][i] += 1
                
    def parse(self, filename):
        """ Fonction créant le dictionnaire de Documents associé à la collection
            de documents entrée en paramètre (fichier filename).
            @param filename: str, nom du fichier .txt à parser
            @return : dict(int, Document)
        """
        # ----- Collection de Documents
        collection = dict()
        
        # ----- Ouverture du fichier et récupération du contenu
        lines = open(filename, 'r').read().splitlines()
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
        
        # ----- Création de la collection de Documents correspondant
        for num, data in dictionnaire.items():
            collection[num] = Document(data)
        
        return collection
    
    def getCollection(self):
        return self.collection
    
    def getAllLinksFrom(self):
        """ Permet de récupérer tous les documents cités par chaque Document.
        """
        return self.index_linksFrom
     
    def getAllLinksTo(self):
        """ Permet de récupérer tous les documents qui citent chaque Document.
        """
        return self.index_linksTo
    
    def getHyperlinksFrom(self, idDoc):
        """ Permet de récupérer tous les documents cités par idDoc.
        """
        return self.index_linksFrom[idDoc]
    
    def getHyperlinksTo(self, idDoc):
        """ Permet de récupérer tous les documents qui citent idDoc.
        """
        return self.index_linksTo[idDoc]