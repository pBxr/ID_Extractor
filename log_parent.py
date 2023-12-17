import time
import os, sys 

class log_parametersClass:

    def __init__(self):

        self.actualTime = time.localtime()
        self.year, self.month, self.day = self.actualTime[0:3]
        self.hour, self.minute, self.second = self.actualTime[3:6]
        self.ID_X_version = "v1.2.0"

    def actualize_logParameters(self):
        self.actualTime = time.localtime()
        self.year, self.month, self.day = self.actualTime[0:3]
        self.hour, self.minute, self.second = self.actualTime[3:6]

        fileNameLog=f"01_ID_Extractor_log_{self.year:4d}-{self.month:02d}-{self.day:02d}_{self.hour:02d}{self.minute:02d}{self.second:02d}.txt"

        fileNameExport=f"02_Export_log_{self.year:4d}-{self.month:02d}-{self.day:02d}_{self.hour:02d}{self.minute:02d}{self.second:02d}.txt"

        return fileNameLog, fileNameExport

    def insert_log_timestamp(self, log):

        log.write(f"Date: {self.day:02d}.{self.month:02d}.{self.year:4d}\n")
        log.write(f"Time: {self.hour:02d}:{self.minute:02d}:{self.second:02d}\n")
        log.write("\n\n")
        
