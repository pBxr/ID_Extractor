import os, sys, sqlite3
import platform

class databaseClass:
    
    def __init__(self):

        self._databases = {
            'cA' : {'dbCall' : 'cA', \
                        'dbDescription' : 'articles that have been checked already', \
                        'dbTableName' : 'list_checked_articles', \
			'dbInit' : 'CREATE TABLE list_checked_articles(publications_ID TEXT PRIMARY KEY, file_name TEXT)'},

            'f2p' : {'dbCall' : 'f2p',\
                        'dbDescription' : 'tables iDAI.field <- -> iDAI.pulications',\
                        'dbTableName' : 'field_to_publications',\
			'dbInit' : 'CREATE TABLE field_to_publications(number INTEGER PRIMARY KEY AUTOINCREMENT,field_ID TEXT, publications_ID TEXT)'},
            
            'g2p' : {'dbCall' : 'g2p',\
                        'dbDescription' : 'tables iDAI.gazetteer <- -> iDAI.pulications', \
                        'dbTableName' : 'gazetteer_to_publications',\
			'dbInit' : 'CREATE TABLE gazetteer_to_publications(number INTEGER PRIMARY KEY AUTOINCREMENT, gazetteer_ID INTEGER, publications_ID TEXT)'},

            'o2p' : {'dbCall' : 'o2p',\
                        'dbDescription' : 'tables iDAI.objects <- -> iDAI.pulications',\
                        'dbTableName' : 'objects_to_publications',\
			'dbInit' : 'CREATE TABLE objects_to_publications(number INTEGER PRIMARY KEY AUTOINCREMENT, objects_ID INTEGER, publications_ID TEXT)'},

            'z2p' : {'dbCall' : 'z2p',\
                        'dbDescription' : 'tables iDAI.bibliography <- -> iDAI.pulications', \
                        'dbTableName' : 'zenon_to_publications',\
			'dbInit' : 'CREATE TABLE zenon_to_publications(number INTEGER PRIMARY KEY AUTOINCREMENT, zenon_ID TEXT, publications_ID TEXT)'},
            }

        self._cursor = ""
        self._connection = ""
        self._path = ""
        self._dbPath = ""
        self._log = []
        self._queryResults = []
        self._programExit = False
        self._dbFromPreviousRunComplete = False
        
        operatingSystem = platform.system()

        cwd = os.getcwd()

        if operatingSystem == "Windows":
                dbPathExists = os.path.exists("db_folder")
                dbExists = os.path.exists("db_folder\\ID_Ex_database.db")
                                 
        if operatingSystem == "Linux":
                dbPathExists = os.path.exists("db_folder")
                dbExists = os.path.exists("db_folder/ID_Ex_database.db")
         
        if not dbPathExists:
            message="No db_folder found.\n"
            print(message)
            self._log.append(message)
            os.makedirs("db_folder")
            message="Created db_folder.\n"
            print(message)
            self._log.append(message)

        else:
            message="Found db_folder.\n\n"
            print(message)
            self._log.append(message)
    
        if operatingSystem == "Windows":
                self._path = cwd+"\\"+"db_folder"+"\\"
        if operatingSystem == "Linux":
                self._path = cwd+'/'+"db_folder"+'/'

        if dbExists == False:
     
            self._dbPath = self._path + "ID_Ex_database.db"

            if not os.path.exists(self._dbPath):
                connection = sqlite3.connect(self._dbPath)
                cursor = connection.cursor()

                message = "Created: " + "ID_Ex_database.db" +"\n"
                print(message)
                self._log.append(message)

                for x, y in self._databases.items():
                    sql = y['dbInit']
                    cursor.execute(sql)
                    connection.commit()
                    message = "Created Table: " + str(y['dbTableName']) +"\n"
                    print(message)
                    self._log.append(message)
                
                connection.close()

        else:
            self._dbPath = self._path + "ID_Ex_database.db"
            self._dbFromPreviousRunComplete = True
            message="Found ID_Ex_database.db.\n"
            print(message)
            self._log.append(message)
      
    def check_if_record_exists(self, articleDOI):
       
        self.open()

        articleExists = False
           
        sql = "SELECT publications_ID FROM list_checked_articles WHERE publications_ID = \"" \
                    + articleDOI + "\""

        self._cursor.execute(sql)
        
        for cursors in self._cursor:
            articleExists = True
              
        self.close()

        return articleExists
    
    def close(self):
        
        self._connection.commit()
        self._connection.close()
        
    def open(self):

        self._connection = sqlite3.connect(self._dbPath)
        self._cursor = self._connection.cursor()
   
    def show_and_export_records(self, chosenDB):

        self.open()

        #(chosenDB was alread checked in main/check_input, so the passed argument should be valid)
        for x, y in self._databases.items():
            if y['dbCall'] == chosenDB: 
              toInsert = y['dbTableName']
                  
        sql = "SELECT * FROM" + " " + toInsert    

        self._cursor.execute(sql)

        self._queryResults.append("%s %s %s" %("\nExport from db", toInsert, "\n\n"))

        result = ""
        
        for res_table in self._cursor:

            for res in res_table:
                result = result + str(res) + ", "

            if len(result)>2:
                result = result[:-2] #cut off the final comma for a clean list

            result = result + "\n"            
            queryResult = "%s %s" % (result, "\n")
            
            self._queryResults.append(queryResult)
            result = ""

        for queryResult in self._queryResults:
            print(queryResult, sep="-")

        self.close()
        
    def update(self, containerArticles):

        self.open()                  

        for containerArticle in containerArticles:
            
            self._cursor.execute("INSERT OR REPLACE INTO list_checked_articles VALUES(?, ?);", \
                                        (containerArticle._articleDOI, containerArticle._fileName))

        for containerArticle in containerArticles:
            for objectsID in containerArticle._objectsIDs:
                self._cursor.execute("INSERT OR REPLACE INTO objects_to_publications VALUES(NULL, ?, ?);", \
                                   (objectsID, containerArticle._articleDOI,))
                containerArticle._log.append("%s %s" %("objectsID extracted:", objectsID))
                
            for zenonID in containerArticle._zenonIDs:
                self._cursor.execute("INSERT OR REPLACE INTO zenon_to_publications VALUES(NULL, ?, ?);", \
                                   (zenonID, containerArticle._articleDOI,))
                containerArticle._log.append("%s %s" %("zenonID extracted:", zenonID))
            
            for gazetteerID in containerArticle._gazetteerIDs:
                self._cursor.execute("INSERT OR REPLACE INTO gazetteer_to_publications VALUES(NULL, ?, ?);", \
                                   (gazetteerID, containerArticle._articleDOI,))
                containerArticle._log.append("%s %s" %("gazetteerID extracted:", gazetteerID))

            for fieldID in containerArticle._fieldIDs:
                self._cursor.execute("INSERT OR REPLACE INTO field_to_publications VALUES(NULL, ?, ?);", \
                                   (fieldID, containerArticle._articleDOI,))
                containerArticle._log.append("%s %s" %("fieldID extracted:", fieldID))
        
        self.close()   
