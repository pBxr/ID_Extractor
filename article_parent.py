import platform
import sys
from bs4 import BeautifulSoup

def clean_list(listIn):

    listIn = list(set(listIn))

    listIn.sort()

    return listIn


class articleIDsClass:
   
    def __init__(self, path, fileName, database, logParameters):

        self.path = ""
        self.fileName = ""
        self.articleDOI = ""
        self.articleRecorded= False
        self.fieldIDs = []
        self.gazetteerIDs = []
        self.objectsIDs = []
        self.zenonIDs = []
        self.soup = ""
        self.logBuffer = []
         
        operatingSystem = platform.system()

        if operatingSystem == "Windows":
            targetFile = path + '\\' + fileName

        if operatingSystem == "Linux":
            targetFile = path + '/' + fileName

        #-- DOIs will be extracted during instantiation           
        try:
            with open(targetFile, 'r', encoding="utf8") as fp:
                  
                self.soup = BeautifulSoup(fp, features="xml")
                
                DOIs = self.soup.find_all('article-id')
                if len(DOIs) <= 0:
                    message = "Caution: \"" + fileName + "\" does not contain an article DOI"
                    self.logBuffer.append(message)
                    self.articleDOI = "NO_DOI"

                for DOI in DOIs:
                    self.articleDOI = DOI.get_text()

            self.path = path
            self.fileName = fileName

            #-- Check if a record already exists for this article
            if not self.articleDOI == 'NO_DOI':
                try:
                    self.articleRecorded = database.check_if_record_exists(self.articleDOI)
                    
                    if self.articleRecorded:
                        self.logBuffer.append(f"{self.articleDOI} - This ID exists already in database \n" \
                                                    "Article skipped.")

                    if not self.articleRecorded:
                        self.logBuffer.append(f"{self.articleDOI} - This article was added " \
                                                    "to existing database")

                except:
                    message = "ERROR: Could not check database"
                    print(message)
                    self.logBuffer.append(message)
                    
            fp.close()
        
        except:
            message = "ERROR: Could not open file, check file name and path."
            print(message)
            self.logBuffer.append(message)
            print("Press enter to quit")
            input()
            sys.exit(0)

    def get_zenonIDs(self):

        zenonIDs = []
        
        zenonLinks = self.soup.find_all('ext-link', {"specific-use":"zenon"})
        for zenonLinkFull in zenonLinks:
            zenonLink = zenonLinkFull.get('xlink:href')

            #-- Get IDs only
            if "https://zenon.dainst.org/Record/" in zenonLink:
                zenonID = zenonLink[32:]
                zenonIDs.append(zenonID)
                self.zenonIDs = clean_list(zenonIDs)                        
                           
    def get_and_separate_others(self):

        linkIDs = []
        gazetteerIDs = []
        objectsIDs = []
        fieldIDs = []

        others = ["extrafeatures", "supplements"]

        for other in others:
            links = self.soup.find_all('ext-link', {"specific-use":other})
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
        self.gazetteerIDs = clean_list(gazetteerIDs)
        self.objectsIDs = clean_list(objectsIDs)
        self.fieldIDs = clean_list(fieldIDs)
