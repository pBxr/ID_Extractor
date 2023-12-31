import os, sys, sqlite3
import time
import platform

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from article_parent import articleIDsClass
from log_parent import log_parametersClass

class guiClass:

    def __init__(self, database, containerArticles, logParameters):

        self.root=tk.Tk()
        
        self.root.title('Welcome to ID_Extractor')
        self.root.iconbitmap("logo.ico")
        self.paddings = {'padx': 10, 'pady': 10}
       
        style = ttk.Style(self.root)
        style.configure("TLabel", font=('Helvetica', 12))
        style.configure("TEntry", background = 'white')
        style.configure("TButton", font=('Helvetica', 12))
        style.configure("TCheckbutton", font=('Helvetica', 10))

        #-- Parameters        
        self.message = tk.StringVar(self.root)
        self.inputString = tk.StringVar(self.root)
        self.path = ""
        self.rowNumber = 0

        
        welcomeMessage = tk.StringVar(self.root)
        welcomeMessageString = "Welcome to ID_EXTRACTOR " + logParameters.ID_X_version + "\n"
        welcomeMessage.set(welcomeMessageString)
        
        ttk.Label(self.root, textvariable = welcomeMessage, style="TLabel").\
                grid(column=0,row = self.rowNumber, sticky ='w', **self.paddings)
   
        #-- First create the non-static head...        
        self.actualize_head(database)

        #-- Now create the checkbuttons...        
        ttk.Label(self.root, text="Choose an export function:").\
            grid(column=0, row = self.rowNumber, sticky ='w', **self.paddings)

        selectedExports = []
        val = []
        i=0
        for x, y in database.databases.items():

            val.append(tk.StringVar(value=0)) #Checkbuttons forced to be off
            check = ttk.Checkbutton(self.root, text = y['dbDescription'], variable = val[i])
            check.grid(column=0,
                    row = self.rowNumber + 1, sticky ='w', **self.paddings)
            
            selectedExports.append(check)
            
            self.rowNumber = self.rowNumber + 1
            i += 1

        #-- Now the menue buttons...            
        ttk.Button(self.root, text = "Run application", style = "TButton",
                   command=lambda: self.start_process(selectedExports,
                                                database, containerArticles, logParameters)).grid(column=0,
                                                row = self.rowNumber + 1,
                                                sticky ='w', **self.paddings)   
        
        ttk.Button(self.root, text = "Exit application", style = "TButton",
                   command=lambda: self.exit_application()).grid(column=1,
                                                row = self.rowNumber + 1,
                                                sticky ='e', **self.paddings)
        
        tk.mainloop()

    def actualize_head(self, database):

        self.rowNumber = 1

        database.check_if_db_exists()
       
        if database.dbFromPreviousRunComplete == True:
            ttk.Label(self.root, text="Found ID_Ex_database.db. Do you wish to run another extraction?", style="TLabel").\
                grid(column=0,row = self.rowNumber, sticky ='w', **self.paddings)

            self.chooseExtraction = tk.StringVar(self.root)
           
            self.extractionSelected = ttk.Radiobutton(self.root, variable = self.chooseExtraction, text = "yes")
            self.extractionSelected.grid(column=1, row = self.rowNumber, sticky ='w', **self.paddings)
            
            self.rowNumber += 1

            self.message.set("If yes, please enter the full path of the directory with .xml article files:")
            
        else:
            extractionSelected = False
            self.rowNumber += 1
            self.message.set("No ID_Ex_database.db found. Please enter the full path of the directory with .xml article files:")
        
        ttk.Label(self.root, textvariable = self.message, style="TLabel").\
            grid(column=0,row = self.rowNumber, sticky ='w', **self.paddings)

        pathEntry = ttk.Entry(self.root, textvariable = self.inputString, style = "TEntry", width = "90").\
            grid(column=1, row = self.rowNumber, sticky ='w', **self.paddings)
        self.rowNumber += 1

    def exit_application(self):
        
        res = messagebox.askokcancel(title="Exit application", message="Exit application?")
        
        if res == True:
            self.root.destroy()    

    def run_extraction(self, database, containerArticles, extraction, logParameters):
            
        if extraction == True:
           
            try:
                files_in_folder = os.scandir(self.path)
            except:
                errMessage = "ERROR: Problem during opening directory " + self.path + ".\nCheck path and restart."
                database.logBuffer.append(errMessage)
                tk.messagebox.showwarning(title="ERROR", \
                                     message=errMessage)   

                self.write_log(database, containerArticles, logParameters)
                self.root.destroy()
                sys.exit(0)

            fileNames = []
            fileNames.clear()

            for fileName in files_in_folder:
                if fileName.name.endswith('.xml'):
                    fileNames.append(fileName.name)
                            
            files_in_folder.close()

            if len(fileNames) <= 0:
                errMessage = "\nERROR: No .xml file found in the current directory. Check entry and restart."
                database.logBuffer.append(errMessage)
                tk.messagebox.showwarning(title="ERROR", message = errMessage)
                self.write_log(database, containerArticles, logParameters)
                self.root.destroy()
                sys.exit(0)

            #-- Now run soup and get IDs
            containerArticles.clear()

            for fileName in fileNames: #(DOIs are extracted during instantiation)
                containerArticles.append(articleIDsClass(self.path, fileName, database, logParameters))
                
            for articleID in containerArticles:
                if not articleID.articleRecorded:
                    articleID.get_zenonIDs()
                    articleID.get_and_separate_others()
              
            #-- Create db log and update databases

            database.update(containerArticles)
         
    def start_process(self, selectedExports, database, containerArticles, logParameters):

        calledFunctions = []
        calledFunction = ""
       
        #-- Check if an extraction is necessary        
        if database.dbFromPreviousRunComplete == True:
            test1 = list(self.extractionSelected.state())
            
            if len(test1) == 0:
                test1.append("Not selected")

            if test1[0] != "Not selected":
                extraction = True
            else:
                extraction = False
        else:
            extraction = True
        
        message="Extraction selected: " + str(extraction) +"\n\n"
        database.logBuffer.append(message)

        #-- Get the export parameters
        i=0
        for x, y in database.databases.items():
            
            test2 = list(selectedExports[i].state())
           
            #There are two values: 'selected' and by default 'alternate' (i. e. the black square)
            #In the following also the default setting (= the black square) is read as a "yes"
            
            if len(test2) == 0:
                test2.append("Not selected")

            if test2[0] != "Not selected":  
                calledFunction = y['dbCall']
                calledFunctions.append(calledFunction)

                message="Following export function(s) selected: " + y['dbDescription'] +"\n"
                
                database.logBuffer.append(message)

            i += 1
         
        self.path = self.inputString.get()
        
        self.run_extraction(database, containerArticles, extraction, logParameters)
        
        
        #--Write log and export files  
        for calledFunction in calledFunctions:
            try:
                database.show_and_export_records(calledFunction)
            except:
                errMessage = "ERROR: Cannot acces database."
                tk.messagebox.showwarning(title="ERROR", message = errMessage)
                database.logBuffer.append(errMessage)
                self.write_log(database, containerArticles, logParameters)
                self.root.destroy()
                sys.exit(0)

        self.write_log(database, containerArticles, logParameters)

        #--Prepare for the next run
        self.inputString.set(None) #Clear the input box for next run
        self.actualize_head(database)
        self.chooseExtraction.set("0") #Clear radiobutton for next run
        self.message.set("Please enter the full path of the directory with .xml article files:")
    
    def write_log(self, database, containerArticles, logParameters):

        fileNameLog, fileNameExport = logParameters.actualize_logParameters()

        operatingSystem = platform.system()
        
        cwd = os.getcwd()

        exists = os.path.exists("_ID_Ex_LOG")

        if not exists:
                os.makedirs("_ID_Ex_LOG")

        if operatingSystem == "Windows":
                logPath = cwd+"\\"+"_ID_Ex_LOG"+"\\"
                
        if operatingSystem == "Linux":
                logPath = cwd+'/'+"_ID_Ex_LOG"+'/'

        #-- First the log
        try:
            log = open(logPath+fileNameLog, "w")
        except:
            print("ERROR: Could not write log. Press enter to quit")
            input()
            sys.exit(0)

        log.write(f"ID_EXTRACTOR {logParameters.ID_X_version} LOG FILE\n\n")
        logParameters.insert_log_timestamp(log)

        for dbLog in database.logBuffer:
            log.write(dbLog)
            
        log.write("\n\n")
        
        for containerArticle in containerArticles:
            log.write(f"Path of extracted repository: {containerArticle.path}\n")
            log.write(f"File name: {containerArticle.fileName} with {containerArticle.articleDOI}\n")
            for entry in containerArticle.logBuffer:
                log.write(f"{entry}\n")
            
            log.write("\n")

        log.close()

        #-- Now the db export file
        if len(database.queryResults) > 0:
            try:
                log = open(logPath+fileNameExport, "w")
            except:
                print("ERROR: Could not write export file. Press enter to quit")
                input()
                sys.exit(0)

            log.write(f"ID_EXTRACTOR {logParameters.ID_X_version} EXPORT FILE\n\n")
            logParameters.insert_log_timestamp(log)
            
            for queryResult in database.queryResults:
                log.write(queryResult)
            
            log.close()

        tk.messagebox.showinfo(title="Information", message="Log file written successfully.")

        #-- Reset 
        actualTime = time.localtime()
        database.reset_for_next_run()
        containerArticles.clear()       
    
