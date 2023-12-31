import os, sys
import platform

from database_parent import databaseClass
from log_parent import log_parametersClass
from gui_parent import guiClass

    
if __name__=='__main__':

    logParameters = log_parametersClass()

    containerArticles = []

    operatingSystem = platform.system()

    if operatingSystem == "Darwin":
        print("ATTENTION: Tool only for WINDOWS or LINUX. Press enter to quit")
        input()
        sys.exit(0)
     
    database = databaseClass()   
 
    window = guiClass(database, containerArticles, logParameters)
        
    sys.exit(0)
