import sqlite3 #qui est utilisé pour interagir avec des bases de données SQLite dans Python.
from flask import g #qui est une variable globale utilisée pour stocker des données pendant la durée de vie d'une requête.
 
def connect_to_database(): # C'est une fonction définie pour se connecter à la base de données SQLite.
    sql = sqlite3.connect("C:/Users/Latitude 5300/Documents/Sekera/Quiz/quizapp.db")
    sql.row_factory = sqlite3.Row
    return sql



def getdatabase():
    if not hasattr(g, "quizapp_db"): #Cette ligne vérifie si l'objet g de Flask possède déjà une connexion à la base de données.
        g.quizapp_db = connect_to_database()
    return g.quizapp_db

#l'objet g de Flask pour stocker la connexion et en s'assurant qu'une seule connexion est établie par requête.

