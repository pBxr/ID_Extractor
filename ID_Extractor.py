from bs4 import BeautifulSoup
import os, sys, sqlite3
import time
import platform

from database_parent import databaseClass


#---------- Definitions classes -------------------------------------------------

class articleIDsClass:
   
    def __init__(self, path, fileName, database):

        self._path = ""
        self._fileName = ""
        self._articleDOI = ""
        self._articleRecorded= False
        self._fieldIDs = []
        self._gazetteerIDs = []
        self._objectsIDs = []
        self._zenonIDs = []
        self._soup = ""
        self._log = []
         
        operatingSystem = platform.system()

        if operatingSystem == "Windows":
            targetFile = path + '\\' + fileName

        if operatingSystem == "Linux":
            targetFile = path + '/' + fileName
                  
        try:
            with open(targetFile, 'r', encoding="utf8") as fp:
                  
                self._soup = BeautifulSoup(fp, features="xml")
                
                DOIs = self._soup.find_all('article-id')
                if len(DOIs) <= 0:
                    message = "Caution: \"" + fileName + "\" does not contain an article DOI"
                    print(message)
                    self._log.append(message)
                    self._articleDOI = "NO_DOI"
                for DOI in DOIs:
                    self._articleDOI = DOI.get_text()

            self._path = path
            self._fileName = fileName

            #------- Check if a record already exists for this article
 
            if not self._articleDOI == 'NO_DOI':
                    
                try:
                    self._articleRecorded = database.check_if_record_exists(self._articleDOI)
                    
                    if self._articleRecorded:
                        self._log.append("%s %s" % (self._articleDOI, "- This ID exists already in database \n" \
                                                    "Article skipped."))

                    if not self._articleRecorded:
                        self._log.append("%s %s" % (self._articleDOI, " - This article was added " \
                                                    "to existing database"))

                except:
                    message = "ERROR: Could not check database"
                    print(message)
                    self._log.append(message)
                
            fp.close()
        
        except:
            message = "ERROR: Could not open file, check file name and path."
            print(message)
            self._log.append(message)
            write_log(self, database)
            print("Press enter to quit")
            input()
            sys.exit(0)

    def get_zenonIDs(self):

        zenonIDs = []
        
        zenonLinks = self._soup.find_all('ext-link', {"specific-use":"zenon"})
        for zenonLinkFull in zenonLinks:
            zenonLink = zenonLinkFull.get('xlink:href')

            #-- Get IDs only
            
            if "https://zenon.dainst.org/Record/" in zenonLink:
                zenonID = zenonLink[32:]
                zenonIDs.append(zenonID)
                self._zenonIDs = clean_list(zenonIDs)                        
                           
    def get_and_separate_others(self):

        linkIDs = []
        gazetteerIDs = []
        objectsIDs = []
        fieldIDs = []

        others = ["extrafeatures", "supplements"]

        for other in others:
            links = self._soup.find_all('ext-link', {"specific-use":other})
            for linkID in links:
                linkIDs.append(linkID.get('xlink:href'))
 
            #-- Get IDs only

            for ID in linkIDs:
                if "https://gazetteer.dainst.org/place/" in ID:
                    gazetteerID = ID[35:]
                    gazetteerIDs.append(gazetteerID)
                    
                if "https://arachne.dainst.org/entity/" in ID:
                    objectsID = ID[34:]
                    objectsIDs.append(objectsID)
                    
                if "https://field.idai.world/document/" in ID:
                    fieldID = ID[34:]
                    fieldIDs.append(fieldID)    

        #-- Sort lists and demove duplicates
                    
        self._gazetteerIDs = clean_list(gazetteerIDs)
        
        self._objectsIDs = clean_list(objectsIDs)
        
        self._fieldIDs = clean_list(fieldIDs)


#---------- Definitions variables and functions ------------------------------------------------

def check_input(dbCall, database):

    functionDetected = False

    if dbCall == "x" or dbCall == "X":
        return True
    
    for x, y in database._databases.items():
        
        if dbCall == (y['dbCall']):
            functionDetected = True
        
    if functionDetected == True:
        return True

    else:
        return False
        
def clean_list(listIn):

    listIn = list(set(listIn))

    listIn.sort()

    return listIn

def insert_log_timestamp(log):

    log.write(f"Date: {day:02d}.{month:02d}.{year:4d}\n")
    log.write(f"Time: {hour:02d}:{minute:02d}:{second:02d}\n")
    log.write("\n\n")
    
def get_parameter(database):

    onlyQuery = False

    path = os.getcwd()

    if database._dbFromPreviousRunComplete == True:
        print("Do you wish to continue with a query of the existing db?\n\n" \
              "Enter \"q\" for query or \"e\" for further extraction of another convolute:")
        res = input()
        while not (res =="q" or res =="Q" or res =="e" or res =="E"):
            print("Input not correct. Please retry.")
            res = input()
                    
        if res == "q" or res =="Q":
            onlyQuery = True

        if res == "e" or res =="E":
            onlyQuery = False

    if onlyQuery == False or database._dbFromPreviousRunComplete == False:
        print("Please enter the full path of the directory with .xml article files:\n")
        path = input()

    print("\n")

    print("Choose an export function by entering one of the following abbreviations...\n")

    for x, y in database._databases.items():
        print(y['dbCall'], " = ", "Export and show the", y['dbDescription'])
    print("x = no additional export")

    check = False

    while not check == True:
        print("... here: ")
        dbCall = input()
        check = check_input(dbCall, database)
        if check == False:
            print("Function does not exists. Please check your input")

    return path, onlyQuery, dbCall
 
def write_log(containerArticles, database):

    cwd = os.getcwd()

    exists = os.path.exists("_ID_Ex_LOG")

    if not exists:
            os.makedirs("_ID_Ex_LOG")

    if operatingSystem == "Windows":
            logPath = cwd+"\\"+"_ID_Ex_LOG"+"\\"
            
    if operatingSystem == "Linux":
            logPath = cwd+'/'+"_ID_Ex_LOG"+'/'

    fileNameLog=f"01_ID_Extractor_log_{year:4d}-{month:02d}-{day:02d}_{hour:02d}{minute:02d}{second:02d}.txt"

    fileNameExport=f"02_Export_log_{year:4d}-{month:02d}-{day:02d}_{hour:02d}{minute:02d}{second:02d}.txt"

    #-- First the log

    try:
        log = open(logPath+fileNameLog, "w")
    except:
        print("ERROR: Could not write log. Press enter to quit")
        input()
        sys.exit(0)

    log.write("%s %s %s" % ("ID_EXTRACTOR", ID_X_version, "LOG FILE\n\n"))
    insert_log_timestamp(log)
    
    for dbLog in database._log:
        log.write(dbLog)

    log.write("\n\n")
    
    for containerArticle in containerArticles:
        log.write("%s %s %s" % ("Path of extracted repository:", containerArticle._path, "\n"))
        log.write("%s %s %s %s %s" % ("File name:", containerArticle._fileName, "with",
                                      containerArticle._articleDOI, "\n"))
        for entry in containerArticle._log:
            log.write("%s %s" % (entry, "\n"))
        
        log.write("\n")

    log.close()

    #-- Now the db export file

    if len(database._queryResults) > 0:

        try:
            log = open(logPath+fileNameExport, "w")
        except:
            print("ERROR: Could not write export file. Press enter to quit")
            input()
            sys.exit(0)

        log.write("%s %s %s" % ("ID_EXTRACTOR", ID_X_version, "EXPORT FILE\n\n"))
        insert_log_timestamp(log)
        
        for queryResult in database._queryResults:
            log.write(queryResult)
        
        log.close()

    
#----------- Main ----------------------------------------------------------------------

#-- Some preconditions       

ID_X_version = "v1.1.1"

operatingSystem = platform.system()
if operatingSystem == "Darwin":
    print("ATTENTION: Tool only for WINDOWS or LINUX. Press enter to quit")
    input()
    sys.exit(0)

actualTime = time.localtime()
year, month, day = actualTime[0:3]
hour, minute, second = actualTime[3:6]

dbExists = False
containerArticles = []

#-- Start
    
print("Welcome to ID_EXTRACTOR", ID_X_version, "\n")

database = databaseClass()  #(Checks during instantiation if db already exists, 
                            #if no db exists it creates all necessary dbs
                            #if one of the necessary dbs from a previous run is missing...
                            #... it returns an exit flag for the following test

path, onlyQuery, dbCall = get_parameter(database)

#-- Run extraction if requested

if onlyQuery == False:

    try:
        files_in_folder = os.scandir(path)
    except:
        message = "ERROR: Problem during opening file. Check file names or path. Press enter to quit"
        print(message)
        input()
        sys.exit(0)

    fileNames = []

    for fileName in files_in_folder:
        if fileName.name.endswith('.xml'):
            fileNames.append(fileName.name)
                    
    files_in_folder.close()

    if len(fileNames) <= 0:
        print("ERROR: No .xml file found in the current directory. Press enter to quit")
        input()
        sys.exit(0)

    #--- Now run soup and get IDs
    
    for fileName in fileNames: #(DOIs are extracted during instantiation)
        containerArticles.append(articleIDsClass(path, fileName, database))
        
    for articleID in containerArticles:
        if not articleID._articleRecorded:
            articleID.get_zenonIDs()
            articleID.get_and_separate_others()
      
    #--- Create db log and update databases

    database.update(containerArticles)

#-- Show and export records if requested

if dbCall != "x":
    database.show_and_export_records(dbCall)

write_log(containerArticles, database)

print("\nTerminated successfully, see _ID_Extractor_log file")
print("Press any key to quit")
input()
sys.exit(0)

