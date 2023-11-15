import os, sys, sqlite3
import platform

class data_base_class:
    
    def __init__(self):

        self._cursors = {}
        self._connections = {}
        self._path = ""
        self._log = []

        exists = os.path.exists("db_folder")
        operatingSystem = platform.system()
        cwd = os.getcwd()    

        if not exists:
            os.makedirs("db_folder")

        if operatingSystem == "Windows":
            self._path = cwd+"\\"+"db_folder"+"\\"
            
        if operatingSystem == "Linux":
            self._path = cwd+'/'+"db_folder"+'/'
             
        if not os.path.exists(self._path+"checked_articles.db"):

            connection_cA = sqlite3.connect(self._path+"checked_articles.db")
            cursor_cA = connection_cA.cursor()

            sql_cA = "CREATE TABLE list_checked_articles(" \
                "publications_ID TEXT PRIMARY KEY, "\
                "file_name TEXT)"
            cursor_cA.execute(sql_cA)
            connection_cA.commit()
            connection_cA.close()

        if not os.path.exists(self._path+"objects_to_publications.db"):

            connection_o2p = sqlite3.connect(self._path+"objects_to_publications.db")
            cursor_o2p = connection_o2p.cursor()

            sql_o2p = "CREATE TABLE objects_to_publications(" \
                "number INTEGER PRIMARY KEY AUTOINCREMENT, " \
                "objects_ID INTEGER, " \
                "publications_ID TEXT)"
            cursor_o2p.execute(sql_o2p)
            connection_o2p.commit()
            connection_o2p.close()

        if not os.path.exists(self._path+"zenon_to_publications.db"):

            connection_z2p = sqlite3.connect(self._path+"zenon_to_publications.db")
            cursor_z2p = connection_z2p.cursor()

            sql_z2p = "CREATE TABLE zenon_to_publications(" \
                "number INTEGER PRIMARY KEY AUTOINCREMENT, " \
                "zenon_ID INTEGER, " \
                "publications_ID TEXT)"
            cursor_z2p.execute(sql_z2p)
            connection_z2p.commit()
            connection_z2p.close()

        if not os.path.exists(self._path+"gazetteer_to_publications.db"):

            connection_g2p = sqlite3.connect(self._path+"gazetteer_to_publications.db")
            cursor_g2p = connection_g2p.cursor()

            sql_g2p = "CREATE TABLE gazetteer_to_publications(" \
                "number INTEGER PRIMARY KEY AUTOINCREMENT, " \
                "gazetteer_ID INTEGER, " \
                "publications_ID TEXT)"
            cursor_g2p.execute(sql_g2p)
            connection_g2p.commit()
            connection_g2p.close()

        if not os.path.exists(self._path+"field_to_publications.db"):  

            connection_f2p = sqlite3.connect(self._path+"field_to_publications.db")
            cursor_f2p = connection_f2p.cursor()

            sql_f2p = "CREATE TABLE field_to_publications(" \
                "number INTEGER PRIMARY KEY AUTOINCREMENT, " \
                "field_ID TEXT, " \
                "publications_ID TEXT)"
            cursor_f2p.execute(sql_f2p)
            connection_f2p.commit()
            connection_f2p.close()

    def check_existance(self, articleDOI):
       
        self.open()

        articleExists = False
           
        sql = "SELECT publications_ID FROM list_checked_articles WHERE publications_ID = \"" \
                    + articleDOI + "\""

        self._cursors["cA"].execute(sql)
        
        for cursors in self._cursors["cA"]:
            articleExists = True
              
        self.close()

        return articleExists

    def open(self):

        connection_cA = sqlite3.connect(self._path + "checked_articles.db")
        cursor_cA = connection_cA.cursor()
        self._cursors.update({"cA" : cursor_cA})
        self._connections.update({"cA" : connection_cA})
            
        connection_o2p = sqlite3.connect(self._path + "objects_to_publications.db")
        cursor_o2p = connection_o2p.cursor()
        self._cursors.update({"o2p" : cursor_o2p})
        self._connections.update({"o2p" : connection_o2p})
        
        connection_z2p = sqlite3.connect(self._path + "zenon_to_publications.db")
        cursor_z2p = connection_z2p.cursor()
        self._cursors.update({"z2p" : cursor_z2p})
        self._connections.update({"z2p" : connection_z2p})
        
        connection_g2p = sqlite3.connect(self._path + "gazetteer_to_publications.db")
        cursor_g2p = connection_g2p.cursor()
        self._cursors.update({"g2p" : cursor_g2p})
        self._connections.update({"g2p" : connection_g2p})
        
        connection_f2p = sqlite3.connect(self._path + "field_to_publications.db")
        cursor_f2p = connection_f2p.cursor()
        self._cursors.update({"f2p" : cursor_f2p})
        self._connections.update({"f2p" : connection_f2p})
        
    def close(self):
        
        for dbName in self._connections:
    
            self._connections[dbName].commit()
            self._connections[dbName].close()
        
    def show_entries(self, chosenDB):

        #-- Caution: Filling up with leading zeroes is not implemented yet

        self.open()
    
        match chosenDB:
            case "cA":
                toInsert = "list_checked_articles"
            case "o2p":
                toInsert = "objects_to_publications"
            case "z2p":
                toInsert = "zenon_to_publications"
            case "g2p":
                toInsert = "gazetteer_to_publications"
            case "f2p":
                toInsert = "field_to_publications"
    
        sql = "SELECT * FROM" + " " + toInsert    

        self._cursors[chosenDB].execute(sql)
        
        for res_table in self._cursors[chosenDB]:
            print(toInsert, res_table, sep=" - ")

    def update(self, containerArticles):

        self.open()                  

        for containerArticle in containerArticles:
            
            self._cursors["cA"].execute("INSERT OR REPLACE INTO list_checked_articles VALUES(?, ?);", \
                                        (containerArticle._articleDOI, containerArticle._fileName))

        for containerArticle in containerArticles:
            for objectsID in containerArticle._objectsIDs:
                self._cursors["o2p"].execute("INSERT OR REPLACE INTO objects_to_publications VALUES(NULL, ?, ?);", \
                                   (objectsID, containerArticle._articleDOI,))
                containerArticle._log.append("%s %s" %("objectsID extracted:", objectsID))
                
            for zenonID in containerArticle._zenonIDs:
                self._cursors["z2p"].execute("INSERT OR REPLACE INTO zenon_to_publications VALUES(NULL, ?, ?);", \
                                   (zenonID, containerArticle._articleDOI,))
                containerArticle._log.append("%s %s" %("zenonID extracted:", zenonID))
            
            for gazetteerID in containerArticle._gazetteerIDs:
                self._cursors["g2p"].execute("INSERT OR REPLACE INTO gazetteer_to_publications VALUES(NULL, ?, ?);", \
                                   (gazetteerID, containerArticle._articleDOI,))
                containerArticle._log.append("%s %s" %("gazetteerID extracted:", gazetteerID))

            for fieldID in containerArticle._fieldIDs:
                self._cursors["f2p"].execute("INSERT OR REPLACE INTO field_to_publications VALUES(NULL, ?, ?);", \
                                   (fieldID, containerArticle._articleDOI,))
                containerArticle._log.append("%s %s" %("fieldID extracted:", fieldID))
        
        self.close()   
