# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#

from error import Error
from controller import *
import libproc

class MemError(Error):
    "Memory-specific error"
    def __init__(self, severity, msg, address, length):
        Error.__init__(self, severity)
        self.msg = msg
        self.address = address
        self.length = length
        
    def __str__(self):
        return "EXCEPTION: " + self.msg + ". Address: " + str(self.address) + ", length: " + str(self.length)
        
class Memory:
    
    @classmethod
    def whenUpdated(cls, fct):
        cls.displayChange = fct

    def __init__(self, board, size):
        self.size = size
        self.wordSize = board.chip.getWordSize()
        self.storage = bytearray([])
        self.controllerList = []
        for _ in range(self.size):
            self.storage.append(0)
            
    def addController(self, controller):
        self.controllerList.append(controller)
                    
    def getSize(self):
        return self.size
            
    def __check(self, address, length):
        if address < 0:
            raise MemError(Error.error, "Negative value", address, length)
            return False
        if (address + length) > self.size:
            raise MemError(Error.error, "Out of memory", address, length)
            return False
        return True
            
    def set(self, address, length, value):
        if (not self.__check(address, length)):
            return
        for i in range(length):
            if (i == length - 1):
                self.storage[address + i] = value % 256
            else:
                self.storage[address + i] = value / 256
                value = value % 256
        for controller in self.controllerList:
            controller.callInput(self, address, length)
        Memory.displayChange(self, address, length, self.wordSize)
  
    def get(self, address, length):
        if (not self.__check(address, length)):
                return 0        
            
        value = 0
        for i in range(length):
            value = (value * 256) + self.storage[address+i]
        return (libproc.ltoi(value, length))
    
    def clear(self):
        for i in range(self.size):
            self.storage[i] = 0

    
    def getByte(self, address):
        return self.storage[address]