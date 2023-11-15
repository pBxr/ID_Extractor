from bs4 import BeautifulSoup
import os, sys, sqlite3
import time
import platform

from data_base_parent import data_base_class


#---------- Definitions variables and classes -------------------------------------------------

class articleIDsClass:
   
    def __init__(self, path, fileName, data_base):

        self._path = ""
        self._fileName = ""
        self._articleDOI = ""
        self._articleRecorded = False
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
                    print("Caution: \"", fileName, "\" does not contain an article DOI")
                    self._articleDOI = "NO_DOI"
                for DOI in DOIs:
                    self._articleDOI = DOI.get_text()

            self._path = path
            self._fileName = fileName
  
            #------- Check if a record already exists for this article
 
            if not self._articleDOI == 'NO_DOI':
                    
                try:
                    self._articleRecorded = data_base.check_existance(self._articleDOI)
                    
                    if self._articleRecorded:
                        self._log.append("%s %s" % (self._articleDOI, "- This ID exists already in data base \n" \
                                                    "Article skipped."))

                    if not self._articleRecorded:
                        self._log.append("%s %s" % (self._articleDOI, " - This article was added " \
                                                    "to existing data base"))
                               
                except:
                    errorMessage="ERROR: Could not check data base"
                    print(errorMessage)
                    self._log.append(errorMessage)
                
            fp.close()
        
        except:
            print("ERROR: Could not open file, check file name and path")
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

        #--- Sort lists and demove duplicates
        self._gazetteerIDs = clean_list(gazetteerIDs)
        
        self._objectsIDs = clean_list(objectsIDs)
        
        self._fieldIDs = clean_list(fieldIDs)


#---------- Definitions functions ------------------------------------------------

def clean_list(listIn):

    listIn = list(set(listIn))

    listIn.sort()

    return listIn
    
def write_log(containerArticles, data_base):

    cwd = os.getcwd()

    exists = os.path.exists("_ID_Ex_LOG")

    if not exists:
            os.makedirs("_ID_Ex_LOG")

    if operatingSystem == "Windows":
            path = cwd+"\\"+"_ID_Ex_LOG"+"\\"
            
    if operatingSystem == "Linux":
            path = cwd+'/'+"_ID_Ex_LOG"+'/'

    fileName=f"_ID_Extractor_log_{year:4d}-{month:02d}-{day:02d}_{hour:02d}{minute:02d}{second:02d}.txt"
    
    try:
        log = open(path+fileName, "w")
    except:
        print("ERROR: Could not write log")
        sys.exit(0)

    log.write("%s %s %s" % ("ID_EXTRACTOR", ID_X_version, "LOG FILE\n\n"))
    log.write(f"Date: {day:02d}.{month:02d}.{year:4d}\n")
    log.write(f"Time: {hour:02d}:{minute:02d}:{second:02d}")
    log.write("\n\n")
    
    for containerArticle in containerArticles:
        log.write("%s %s %s" % ("Path of extracted repository:", containerArticle._path, "\n"))
        log.write("%s %s %s %s %s" % ("File name:", containerArticle._fileName, "with",
                                      containerArticle._articleDOI, "\n"))
        for entry in containerArticle._log:
            log.write("%s %s" % (entry, "\n"))
        
        log.write("\n")
    
    log.close

       
#----------- Main ----------------------------------------------------------------------
       
ID_X_version = "v1.0.0"
actualTime = time.localtime()
year, month, day = actualTime[0:3]
hour, minute, second = actualTime[3:6]

operatingSystem = platform.system()

if operatingSystem == "Darwin":
    print("ATTENTION: Tool only for WINDOWS or LINUX") 

data_base = data_base_class()

print("Welcome to ID_EXTRACTOR", ID_X_version, "\n\nPlease choose a directory by entering the full path:\n")

path = input()


#---- Can be switched on for testing purposes
"""
if operatingSystem == "Windows":
    path = "###"

if operatingSystem == "Linux":
    path = "###"
"""   

print("You have chosen following path:", path, "\n")

#--- Extract names of all .xml-files

try:
    files_in_folder = os.scandir(path)
except:
    print("ERROR: Problem during opening file. Check file names or path.")
    quit()

fileNames = list()

for fileName in files_in_folder:
    if fileName.name.endswith('.xml'):
        fileNames.append(fileName.name)
                
files_in_folder.close()

if len(fileNames) <= 0:
    print("ERROR: No .xml-file found in the current directory.")
    quit()

#--- Now run soup and get IDs

containerArticles = list()

for fileName in fileNames:
    containerArticles.append(articleIDsClass(path, fileName, data_base))
    
  
for articleID in containerArticles:
    if not articleID._articleRecorded:
        articleID.get_zenonIDs()
        articleID.get_and_separate_others()
    
#--- Create log and update data bases

data_base.update(containerArticles)

#---- Can be switched on for testing purposes - more elaborate functions in the next version...
#data_base.show_entries("cA")
#data_base.show_entries("o2p")
#data_base.show_entries("z2p")
#data_base.show_entries("g2p")
#data_base.show_entries("f2p")

write_log(containerArticles, data_base)

print("\nTerminated successfully, see _ID_Extractor_log file")



