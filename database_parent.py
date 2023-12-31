import os, sys, sqlite3
import platform

class databaseClass:
    
    def __init__(self):

        self.databases = {
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

        self.cursor = ""
        self.connection = ""
        self.path = ""
        self.dbPath = ""
        self.dbSize = ""
        self.logBuffer = []
        self.queryResults = []
        self.programExit = False
        self.dbFromPreviousRunComplete = False

    def actualize_nr_of_entries(self):

            self.open()

            sql = "SELECT COUNT(*) FROM list_checked_articles"

            try:
                self.cursor.execute(sql)
            except:
                errMessage = "ERROR: Cannot acces database."
                self.logBuffer.append(errMessage)
                print(errMessage)   
                sys.exit(0)

            for res_table in self.cursor:
                for res in res_table:
                    self.dbSize = res

            self.close()
 
    def check_if_db_exists(self):
        self.dbFromPreviousRunComplete = False

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
            self.logBuffer.append(message)

            os.makedirs("db_folder")

            message="Created db_folder.\n"
            self.logBuffer.append(message)

        else:
            message="Found db_folder.\n\n"
            self.logBuffer.append(message)
    
        if operatingSystem == "Windows":
                self.path = cwd+"\\"+"db_folder"+"\\"
        if operatingSystem == "Linux":
                self.path = cwd+'/'+"db_folder"+'/'

        if dbExists == False:
     
            self.dbPath = self.path + "ID_Ex_database.db"

            if not os.path.exists(self.dbPath):
                connection = sqlite3.connect(self.dbPath)
                cursor = connection.cursor()

                message = "Created: " + "ID_Ex_database.db" +"\n"
                self.logBuffer.append(message)

                for x, y in self.databases.items():
                    sql = y['dbInit']
                    cursor.execute(sql)
                    connection.commit()
                    message = "Created Table: " + str(y['dbTableName']) +"\n"
                    self.logBuffer.append(message)
                
                connection.close()

        else:
            self.dbPath = self.path + "ID_Ex_database.db"
            self.dbFromPreviousRunComplete = True
            message="Found ID_Ex_database.db.\n\n"
            self.logBuffer.append(message)

    def check_if_record_exists(self, articleDOI):
       
        self.open()

        articleExists = False

        try:   
            sql = "SELECT publications_ID FROM list_checked_articles WHERE publications_ID = \"" \
                    + articleDOI + "\""
        
            self.cursor.execute(sql)
        except:
            errMessage = "\nERROR: Could not check database. Check and restart."
            self.logBuffer.append(errMessage)
            tk.messagebox.showwarning(title="ERROR", message = errMessage)
            
            self.root.destroy()
            sys.exit(0)
            
        for cursors in self.cursor:
            articleExists = True

              
        self.close()

        return articleExists
    
    def close(self):
        
        self.connection.commit()
        self.connection.close()
        
    def open(self):
 
        self.connection = sqlite3.connect(self.dbPath)
        self.cursor = self.connection.cursor()
    
    def reset_for_next_run(self):
        self.logBuffer = []
        self.queryResults.clear()
  
    
    def show_and_export_records(self, chosenDB):

        self.open()

        #(chosenDB was alread checked in main/check_input, so the passed argument should be valid)
        for x, y in self.databases.items():
            if y['dbCall'] == chosenDB: 
              toInsert = y['dbTableName']
                  
        sql = "SELECT * FROM" + " " + toInsert    

        try:
            self.cursor.execute(sql)
        except:
            errMessage = "ERROR: Cannot acces database."
            self.logBuffer.append(errMessage)
            print(errMessage)   
            sys.exit(0)

        self.queryResults.append(f"\nExport from db {toInsert}\n\n")

        result = ""
        
        for res_table in self.cursor:

            for res in res_table:
                result = result + str(res) + ", "

            if len(result)>2:
                result = result[:-2] #cut off the final comma for a clean list

            result = result + "\n"            
            queryResult = f"{result}\n"
            
            self.queryResults.append(queryResult)
            result = ""

        self.close()

               
    def update(self, containerArticles):

        self.open()                  

        for containerArticle in containerArticles:
            
            self.cursor.execute("INSERT OR REPLACE INTO list_checked_articles VALUES(?, ?);", \
                                        (containerArticle.articleDOI, containerArticle.fileName))

        for containerArticle in containerArticles:
            for objectsID in containerArticle.objectsIDs:
                self.cursor.execute("INSERT OR REPLACE INTO objects_to_publications VALUES(NULL, ?, ?);", \
                                   (objectsID, containerArticle.articleDOI,))
                containerArticle.logBuffer.append(f"objectsID extracted: {objectsID}")
                
            for zenonID in containerArticle.zenonIDs:
                self.cursor.execute("INSERT OR REPLACE INTO zenon_to_publications VALUES(NULL, ?, ?);", \
                                   (zenonID, containerArticle.articleDOI,))
                containerArticle.logBuffer.append(f"zenonID extracted: {zenonID}")
            
            for gazetteerID in containerArticle.gazetteerIDs:
                self.cursor.execute("INSERT OR REPLACE INTO gazetteer_to_publications VALUES(NULL, ?, ?);", \
                                   (gazetteerID, containerArticle.articleDOI,))
                containerArticle.logBuffer.append(f"gazetteerID extracted: {gazetteerID}")

            for fieldID in containerArticle.fieldIDs:
                self.cursor.execute("INSERT OR REPLACE INTO field_to_publications VALUES(NULL, ?, ?);", \
                                   (fieldID, containerArticle.articleDOI,))
                containerArticle.logBuffer.append(f"fieldID extracted: {fieldID}")
        
        self.close()

        self.actualize_nr_of_entries()
        
