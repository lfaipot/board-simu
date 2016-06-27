# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#

import imp
import os
import shlex

from memory import Memory, MemError
from config import Config
from controller import Controller
from program import Program, ProgramError

class Board:
    """
    Board definition and handling
    """
    
    
    @staticmethod
    def getList():
        """
        Return the list of boards described into the configuration file
        """
        boardDir = Config.getBoardDir()
        boardFile = os.path.join(boardDir, "board_description.cfg")
        Board.config = Config(boardFile)
        boardList = Board.config.getItems("Boards")
        return boardList
        
    def __init__(self, boardName, display):
        """
        initialize a board by loading its definition
        
        @param boardName: name of board in board description file
        @type  boardName: string
        @param display:   where to display board
        @type  display:   Windows
        """
        self.display = display
        self.deviceModuleList = []
        self.program    = None
        self.boardHelp  = None
        self.archHelp   = None
        
        self.loadDefinition(boardName)

   
    def loadDefinition(self, boardName):
        """
        load the board definition from the definition file
        
        @param boardName: name of board to look for in the description file
        @type  boardName: string
        """
        items = Board.config.getItems(boardName)
        self.deviceList = []
        for item in items:
            name = item[0]
            value = item[1]
            if name == "arch":
                self.archName = value
            elif name == "memory":
                if (value == "max"):
                    self.memorySize = -1
                else:
                    self.memorySize = int(value)
            elif name[0:6] == "device":
                device = shlex.split(value, "#")
                self.deviceList.append(device)
            elif name == "help":
                fileName = os.path.join(Config.getBoardDir(), value)
                if os.path.isfile(fileName):
                    self.boardHelp = fileName
    
    def build(self):
        """
        Build the board:
        . load its architecture: chip with registers, opcodes and so on
        . load its controller definition and initialize them
        . initialize its memory
        . attach controllers to their I/O addresses
        """
        archDir = Config.getArchDir()
        archPath = os.path.join(archDir, "arch_" + self.archName + ".py")
        self.archModule = imp.load_source(self.archName, archPath)
        self.archHelp = os.path.join(archDir, "arch_" + self.archName + ".html")
        if not os.path.isfile(self.archHelp):
            self.archHelp = None
        self.chip = self.archModule.Chip()
        if (self.memorySize == -1):
            self.memorySize = 2 ** (self.chip.getAddressSize() * 8)
        self.controller = Controller(self.display)
        self.controller.loadDeviceList()
        self.memory = Memory(self, self.memorySize)
        self.memory.addController(self.controller)
         
        for device in self.deviceList:
            self.deviceModuleList.append(self.controller.createDevice(device))
            
    def clear(self):
        """
        Clear the board: reset memory and chip (PC, SP, other registers and so on)
        """
        self.memory.clear()
        self.chip.clear()
            
    def delete(self):
        """
        Delete the board: remove attached controllers
        """
        self.controller.delete()
 
    def loadProgram(self, fileName):
        """
        Load the program in memory
        
        @param filename: file containing the code to execute       
        @type  filename: string
        """
        try:
            self.program = Program()
            self.program.load(fileName, self)
            self.chip.setEndProgram(False)
            return True
        except MemError as e:
            e.display()
            return False
        except ProgramError:
            return False