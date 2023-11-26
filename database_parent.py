import os, sys, sqlite3
import platform

class databaseClass:
    
    def __init__(self):

        self._databases = {
            'cA' : {'dbName' : 'checked_articles.db', 'dbCall' : 'cA', \
                        'dbDescription' : 'articles that have been checked already', \
                        'dbTableName' : 'list_checked_articles', \
			'dbInit' : 'CREATE TABLE list_checked_articles(publications_ID TEXT PRIMARY KEY, file_name TEXT)'},

            'f2p' : {'dbName' : 'field_to_publications.db', 'dbCall' : 'f2p',\
                        'dbDescription' : 'tables iDAI.field <- -> iDAI.pulications',\
                        'dbTableName' : 'field_to_publications',\
			'dbInit' : 'CREATE TABLE field_to_publications(number INTEGER PRIMARY KEY AUTOINCREMENT,field_ID TEXT, publications_ID TEXT)'},
            
            'g2p' : {'dbName' : 'gazetteer_to_publications.db', 'dbCall' : 'g2p',\
                        'dbDescription' : 'tables iDAI.gazetteer <- -> iDAI.pulications', \
                        'dbTableName' : 'gazetteer_to_publications',\
			'dbInit' : 'CREATE TABLE gazetteer_to_publications(number INTEGER PRIMARY KEY AUTOINCREMENT, gazetteer_ID INTEGER, publications_ID TEXT)'},

            'o2p' : {'dbName' : 'objects_to_publications.db', 'dbCall' : 'o2p',\
                        'dbDescription' : 'tables iDAI.objects <- -> iDAI.pulications',\
                        'dbTableName' : 'objects_to_publications',\
			'dbInit' : 'CREATE TABLE objects_to_publications(number INTEGER PRIMARY KEY AUTOINCREMENT, objects_ID INTEGER, publications_ID TEXT)'},

            'z2p' : {'dbName' : 'zenon_to_publications.db', 'dbCall' : 'z2p',\
                        'dbDescription' : 'tables iDAI.bibliography <- -> iDAI.pulications', \
                        'dbTableName' : 'zenon_to_publications',\
			'dbInit' : 'CREATE TABLE zenon_to_publications(number INTEGER PRIMARY KEY AUTOINCREMENT, zenon_ID TEXT, publications_ID TEXT)'},
            }           #Caution: zenon_ID is of type TEXT to handle the required leading zeros

        self._cursors = {}
        self._connections = {}
        self._path = ""
        self._log = []
        self._queryResults = []
        self._programExit = False
        self._dbFromPreviousRunComplete = False
        self._noDbExists = False

        dbPathExists = os.path.exists("db_folder")

        operatingSystem = platform.system()

        cwd = os.getcwd()

        if not dbPathExists:
            os.makedirs("db_folder")
            message="No database found. Created db_folder\n"
            print(message)
            self._log.append(message)
            
        else:
            message="Found db_folder\n"
            print(message)
            self._log.append(message)

            #Checks if all necessary dbs already exists, 
            #if dbs are incomplete saves an exit flag in self._programExit
            self.check_existingDB()

        if self._programExit == False:
     
            if operatingSystem == "Windows":
                self._path = cwd+"\\"+"db_folder"+"\\"
                
            if operatingSystem == "Linux":
                self._path = cwd+'/'+"db_folder"+'/'

            for x, y in self._databases.items():
                dbPath = self._path + y['dbName']

                if not os.path.exists(dbPath):
                    connection = sqlite3.connect(dbPath)
                    cursor = connection.cursor()
                    sql = y['dbInit']
                    cursor.execute(sql)
                    connection.commit()
                    connection.close()
                    message = "Created: " + str(y['dbName']) +"\n"
                    print(message)
                    self._log.append(message)

    def check_existingDB(self):

        mandatoryDBs = []
        missingDBs = []

        for x, y in self._databases.items():
            mandatoryDBs.append(y['dbName'])
             
        for mandatoryDB in mandatoryDBs:
            testpath = "db_folder" + "\\"+ mandatoryDB
            exists = os.path.exists(testpath)
            if not exists:
               missingDBs.append(mandatoryDB) 

        if len(missingDBs) > 0 and len(missingDBs) < 5:
            message = "\nCAUTION: One or more databases are missing:\n"
            print(message)
            self._log.append(message)
            for missingDB in missingDBs:
                message = missingDB + "\n"
                print(message)
                self._log.append(message)
            self._programExit = True
                       
        if len(missingDBs) == 5:
            message = "No databases detected"
            print(message)
            self._log.append(message) 
            self._programExit = False
            self._noDbExists = True

        if len(missingDBs) == 0:
            message = "All 5 databases exist.\nCAUTION: If an article is recorded already it will not be extracted again."
            print(message)
            self._log.append(message) 
            self._programExit = False
            self._dbFromPreviousRunComplete = True

    def check_if_record_exists(self, articleDOI):
       
        self.open()

        articleExists = False
           
        sql = "SELECT publications_ID FROM list_checked_articles WHERE publications_ID = \"" \
                    + articleDOI + "\""

        self._cursors["cA"].execute(sql)
        
        for cursors in self._cursors["cA"]:
            articleExists = True
              
        self.close()

        return articleExists
    
    def close(self):
        
        for dbName in self._connections:
            self._connections[dbName].commit()
            self._connections[dbName].close()
        
    def open(self):

        #-- Opens all databases

        for x, y in self._databases.items():
            dbPath = self._path + y['dbName']
        
            connection = sqlite3.connect(dbPath)
            cursor = connection.cursor()

            self._cursors.update({str(y['dbCall']) : cursor})
            self._connections.update({str(y['dbCall']) : connection})

    def show_and_export_records(self, chosenDB):

        self.open()

        #(chosenDB was alread checked in main/check_input, so the passed argument should be valid)
        for x, y in self._databases.items():
            if y['dbCall'] == chosenDB: 
              toInsert = y['dbTableName']
                  
        sql = "SELECT * FROM" + " " + toInsert    

        self._cursors[chosenDB].execute(sql)

        self._queryResults.append("%s %s %s" %("\nExport from db", toInsert, "\n\n"))

        result = ""
        
        for res_table in self._cursors[chosenDB]:

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
