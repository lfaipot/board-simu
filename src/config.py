# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#

import os
import trace
import ConfigParser

class Config:
    
    __maxRecentFiles = 5
    
    @staticmethod
    def currentDir():
        currentDir = os.path.dirname(os.path.abspath(__file__))
        return currentDir
    
    @staticmethod
    def getArchDir():
        currentDir = os.path.dirname(os.path.abspath(__file__))
        archPath = os.path.join(currentDir, "hardware", "arch")
        return archPath
    
    @staticmethod
    def getBoardDir():
        currentDir = os.path.dirname(os.path.abspath(__file__))
        boardPath = os.path.join(currentDir, "hardware", "board")
        return boardPath
    
    @staticmethod
    def getDeviceDir():
        currentDir = os.path.dirname(os.path.abspath(__file__))
        devicePath = os.path.join(currentDir, "hardware", "device")
        return devicePath
    
    @staticmethod
    def getDocDir():
        currentDir = os.path.dirname(os.path.abspath(__file__))
        docPath = os.path.join(currentDir, "..", "doc")
        return docPath
    
    def __init__(self, fileName):
        home = os.path.expanduser("~")
        self.configFileName = os.path.join(home, fileName)
        trace.debug(1, "Using configuration file " + self.configFileName)
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.configFileName)
        
    def write(self):
        with open(self.configFileName, 'wb') as configfile:
            self.config.write(configfile)
            
    def getOption(self, section, option):
        if self.config.has_section(section):
            if self.config.has_option(section, option):
                return self.config.get(section, option)
        return ""
            
    def setOption(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
        
    def getItems(self, section):
        if self.config.has_section(section):
            return self.config.items(section)
        return ()
        
    def setItems(self, section, prefix, lst):
        if not self.config.has_section(section):
            self.config.add_section(section)
        count = 0
        for elem in lst:
            self.setOption(section, prefix + "_" + str(count), elem)
            count +=1
    
    def getLastOpenedFile(self):
        return self.getOption("Recent_Files", "path_0")
    
    def setRecentFiles(self, fileName):
        recentFiles = self.getRecentFiles()
        if fileName in recentFiles:
            recentFiles.remove(fileName)
        length = len(recentFiles)
        if length >= self.__maxRecentFiles:
            recentFiles = recentFiles[0:length-1]
        recentFiles.insert(0, fileName)
        self.setItems("Recent_Files", "path", recentFiles)
        self.write()

    def getRecentFiles(self):
        lst = self.getItems("Recent_Files")
        recentFiles = []
        for _, fileName in lst:
            recentFiles.append(fileName)
        return recentFiles
            
