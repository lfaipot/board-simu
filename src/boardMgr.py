# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#

import sys
import time
from PyQt4 import QtGui, QtCore
from config import Config

import libproc

from boardMgrUi import Ui_BoardMgr

from board import Board
from memory import Memory
from processor import Processor, Register, Indicator
from error import *
import helpMgr


class BoardMgr(QtGui.QMainWindow, Ui_BoardMgr):
    
    # number of bytes displayed per line in the memory windows
    __memoryBytesPerLine = 8
    
    # used to display messages stopping execution
    def displayCritical(self, exception):
        QtGui.QMessageBox.critical(
                          self,
                          'Critical',
                          str(exception)
                          )
        
    
    def __init__(self, boardName, boardLabel, app, parent):
        super(BoardMgr, self).__init__(parent)
        self.app = app
        self.parent = parent
        
        self.setupUi(self)
        self.board = Board(boardName, parent)
        self.setWindowTitle(boardLabel)

        x = self.parent.config.getOption("BOARD WINDOW", "X")
        y = self.parent.config.getOption("BOARD WINDOW", "Y")
        window = self.geometry()

        valX = window.x()
        if x != "":
            valX = int(x)
        valY = window.y()
        if y != "":
            valY = int(y)
        self.setGeometry(QtCore.QRect(valX, valY, window.width(), window.height()))
        self.show()
        
        # initialize the board content: processor instructions, memory and controllers
        self.board.build()
        # action of the board window
        self.defineActions()
        
        # values represent 1/10 s
        self.sleepMin = 10 # 0.1 between each instruction
        self.sleepMax = 200 # 2 s between each instruction
        self.sleepSingleStep = 20 # slider precision

        # initialize speed slider
        self.speedSlider.setValue(100)
        self.speedSlider.setMinimum(self.sleepMin)
        self.speedSlider.setMaximum(self.sleepMax)
        self.speedSlider.setSingleStep(self.sleepSingleStep)
        self.speedSlider.setPageStep(40)
        
        if self.board.boardHelp:
            self.actionAboutBoard.setEnabled(True)
        else:
            self.actionAboutBoard.setEnabled(False)
        if self.board.archHelp:
            self.actionAboutProcessor.setEnabled(True)
        else:
            self.actionAboutProcessor.setEnabled(False)
            
        self.displayMemory(self.board.memory, self.board.chip.getWordSize(), self.board.chip.getAddressSize())
        self.displayRegister(self.board)
        self.displayIndicator(self.board)

        Error.whenHappen(self.displayCritical)
        Register.whenUpdated(self.updateRegister)
        Indicator.whenUpdated(self.updateIndicator)
        Memory.whenUpdated(self.updateMemory)
        Processor.whenUpdated(self.displayInstruction)

    #
    # Predefined Windows Management functions
    #   
    def delete(self):
        self.board.delete()
        self.deleteLater()
        
    def closeEvent(self, event):
        self.parent.quit()
        
    def moveEvent(self, oldPos):
        self.parent.config.setOption("BOARD WINDOW", "X", str(self.x()))
        self.parent.config.setOption("BOARD WINDOW", "Y", str(self.y()))
        self.parent.config.write()
            
    def quit(self):
        print "quit"
        QtGui.qApp.quit()
        
    def defineActions(self):
        QtCore.QObject.connect(self.runButton, QtCore.SIGNAL('clicked()'), self.runProgram)
        QtCore.QObject.connect(self.stepButton, QtCore.SIGNAL('clicked()'), self.stepProgram)
        QtCore.QObject.connect(self.stopButton, QtCore.SIGNAL('clicked()'), self.stopProgram)
        QtCore.QObject.connect(self.hexaMode, QtCore.SIGNAL('toggled(bool)'), self.changeHexaMode)
        QtCore.QObject.connect(self.speedSlider, QtCore.SIGNAL('valueChanged(int)'), self.changeSpeed)
        

        self.actionAboutProcessor.triggered.connect(self.displayAboutProcessor)
        self.actionAboutBoard.triggered.connect(self.displayAboutBoard)
        self.hexaMode = False

    # only address display
    def changeHexaMode(self, toogled):
        self.hexaMode = toogled
        self.updateMemoryAddress(self.board.memory, self.board.chip.getAddressSize())
        if (self.board.program):
            self.updateProgramAddress(self.board.program)
            
    #
    # Speed slider: adjust the sleep duration between the execution of 2 instructions
    #
    def changeSpeed(self, value):
        # value in 1/10 s
        self.sleep = (self.sleepMax + self.sleepMin - value) * 0.1 
    
    def displayAboutProcessor(self):
        helpMgr.display(self.board.archHelp)
    
    def displayAboutBoard(self):
        helpMgr.display(self.board.boardHelp)
    
    #
    # load a new program
    #
    def processFile(self, fileName):
        self.board.clear()
        self.displayMemory(self.board.memory, self.board.chip.getWordSize(), self.board.chip.getAddressSize())
        self.instructionTable.clear()
        
        if (self.board.loadProgram(fileName)):
            self.runButton.setEnabled(True)
            self.stepButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            self.board.chip.PC.set(self.board.program.getCodeBase())
            self.initProgram(self.board.program)
            return True
        else:
            self.runButton.setEnabled(False)
            self.stepButton.setEnabled(False)
            self.stopButton.setEnabled(False)
            return False
        
    #
    # PROGRAM
    #
        
    def initProgram(self, program):
        self.stop = False
        self.end = False
        self.displayProgram(program)

        
    def runProgram(self):
        self.stop = False
        self.runButton.setEnabled(False)
        self.stepButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        while (not self.stop and not self.end):
            self.executeNext(self.board)
            # need 2 calls on Linux to get a refresh of windows (unknown reason)
            self.app.processEvents()
            self.app.processEvents()          
            # sleep without preventing interaction
            # - sleep is in 1/10 seconds so loop until required time
            # - note that sleep time can be changed during the loop
            #   so don't use range in order to access updated value
            #   no data locking to avoid complexity
            loop = 0
            while loop < self.sleep:
                time.sleep(0.1)
                self.app.processEvents()
                loop += 1
        self.stopProgram()
        
                    
    def stepProgram(self):
        self.runButton.setEnabled(True)
        self.stepButton.setEnabled(True)
        self.stopButton.setEnabled(False)
 
        self.executeNext(self.board)
            
    def stopProgram(self):
        self.stop = True
        self.stopButton.setEnabled(False)
        if not self.end:
            self.runButton.setEnabled(True)
            self.stepButton.setEnabled(True)
        
    def executeNext(self, board):
        
        # reset all indicators of previous changes for memory, register and status
        self.cleanMemoryMarker(self.board.memory)
        self.cleanRegisterMarker()
        self.cleanIndicatorMarker()
        
        try:
            self.end = self.board.chip.executeNext(self.board)
            return
        except Error as e:
            self.end = True
            self.stop = False
            self.runButton.setEnabled(False)
            self.stepButton.setEnabled(False)
            self.stopButton.setEnabled(False)
            e.display()
        finally:
            if (self.end):
                self.runButton.setEnabled(False)
                self.stepButton.setEnabled(False)
                self.stopButton.setEnabled(False)



    #
    # MEMORY
    #
    
    def displayMemory(self, memory, wordSize, addressSize):
        size = memory.getSize()
        #Sself.memoryTable.setStyleSheet('font-size: 12pt; font-family: Courier;')
        self.nbMemoryRow = size / BoardMgr.__memoryBytesPerLine
        self.nbMemoryCol = (BoardMgr.__memoryBytesPerLine / wordSize)
        self.memoryTable.setRowCount(self.nbMemoryRow)
        self.memoryTable.setColumnCount(self.nbMemoryCol)
        
        #size in pixels
        addressLength = 60
        quartLength = 32
        hFiller = 30
        mini = addressLength
        
        for col in range(self.nbMemoryCol):
            size = quartLength * wordSize
            self.memoryTable.setColumnWidth(col, size)
            mini += size

        self.memoryTable.setMinimumSize(QtCore.QSize(mini + hFiller, 0))
        self.memoryTable.setMaximumSize(QtCore.QSize(mini + hFiller, 10000))
          
        
        # populate with data
        initList = []
        for row in range(self.nbMemoryRow):
            col = 0
            while (col < self.nbMemoryCol):
                item = QtGui.QTableWidgetItem("")
                self.memoryTable.setItem(row, col, item)
                mem = memory.get(row * BoardMgr.__memoryBytesPerLine + col, wordSize)
                value = libproc.ltoh(mem, wordSize)
                item = QtGui.QTableWidgetItem(value)
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
                self.memoryTable.setItem(row, col, item)
                col += 1
                initList.append("")
                
        # initialize address  
        self.memoryTable.setVerticalHeaderLabels(initList)
        self.updateMemoryAddress(memory, addressSize)    
        
          
    def updateMemoryAddress(self, memory, addressSize):
        addressList = []
        for row in range(self.nbMemoryRow):
            if self.hexaMode:
                address = libproc.ltoh(row * BoardMgr.__memoryBytesPerLine, 2)
            else:
                address = str((row * BoardMgr.__memoryBytesPerLine));            
            addressList.append(address)
            self.memoryTable.verticalHeaderItem(row).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)    
        self.memoryTable.setVerticalHeaderLabels(addressList)
        
            
    def updateMemory(self, memory, address, length, wordSize = 1):
        size = memory.getSize()
        i = address
        while (i < size) & (i < address + length):
            row = i / BoardMgr.__memoryBytesPerLine
            col = i - (row * BoardMgr.__memoryBytesPerLine)
            mem = memory.get(row * BoardMgr.__memoryBytesPerLine + col, wordSize)
            value = libproc.ltoh(mem, wordSize)
            self.memoryTable.item(row, col).setText(value)
            self.memoryTable.item(row, col).setBackground(QtGui.QColor(0,160,0))
            i += wordSize
    
    def cleanMemoryMarker(self, memory):
        for row in range(self.nbMemoryRow):
            for col in range(self.nbMemoryCol):
                self.memoryTable.item(row, col).setBackground(QtGui.QColor(255,255,255))
    
    #
    # INSTRUCTION
    #
    
    def displayProgram(self, program):
        
        # size in pixels
        addressCol  = 30
        labelCol    = 150
        codeCol     = 60
        operandCol  = 150
        hFiller     = 20
        total       = addressCol + labelCol + codeCol + operandCol + hFiller
        
        self.instructionTable.setMinimumSize(QtCore.QSize(total, 16777215))
        self.instructionTable.setColumnCount(3)
        self.instructionTable.setColumnWidth(0,labelCol)
        self.instructionTable.setColumnWidth(1,codeCol)
        self.instructionTable.setColumnWidth(2,operandCol)
        
        row = 0
        instructionList = program.getInstructionList()
        self.instructionTable.setRowCount(len(instructionList))
        
        initList = []
        self.updateProgramAddress(program)
        for inst in instructionList:
            for col in range(3):
                if col == 0:
                    value = str(inst.getLabel())
                if col == 1:
                    value = inst.getMnemonic()
                if col == 2:
                    value = inst.getOperand()
                item = QtGui.QTableWidgetItem(value)
                self.instructionTable.setItem(row, col, item)
            row +=1
            initList.append("")
        
        self.instructionTable.setVerticalHeaderLabels(initList)
        self.updateProgramAddress(program)

                
    def updateProgramAddress(self, program):
        addressList = []
        row = 0
        instructionList = program.getInstructionList()
        for inst in instructionList:
            if self.hexaMode:
                value = libproc.ltoh(inst.getAddress(), self.board.chip.getAddressSize())
            else: 
                value = str(inst.getAddress())
            addressList.append(value)
            row +=1
        self.instructionTable.setVerticalHeaderLabels(addressList)
            
    #
    # highlight the instruction line corresponding to the program counter
    #
    def displayInstruction(self, pc):
        #if we exit from the loop without setting rowToDisplay
        # this is the last instruction of the program
        rowToDisplay = self.instructionTable.rowCount() - 1
        
        # look for instruction based on its address
        for row in range(self.instructionTable.rowCount()):
            inst = self.board.program.getInstruction(row)
            address = inst.getAddress()
            # be sure to display the last with this address
            # in case there is a label before an instruction (same address)
            # then stop only when going too far
            if (address > pc):
                rowToDisplay = row - 1
                break

        self.instructionTable.selectRow(rowToDisplay)
        
    #
    # REGISTER
    #
    
    def displayRegister(self, board):
        registerList = board.chip.getRegisterList()

        nameCol = 40
        valCol = 80
        hFiller = 2
        width = nameCol + 2 * valCol 
        height = (len(registerList) * 30) + hFiller
        
        self.registerTable.setMinimumSize(QtCore.QSize(width, height))
        self.registerTable.setMaximumSize(QtCore.QSize(width, height))
 
        self.registerTable.setRowCount(len(registerList))
        self.registerTable.setColumnCount(2)
        
        nameList = []
        for reg in registerList:
            nameList.append(reg.getName())
        self.registerTable.setVerticalHeaderLabels(nameList)
        
        count = 0
        for reg in registerList:
            self.registerTable.setColumnWidth(count, valCol)
            
            self.registerTable.verticalHeaderItem(count).setToolTip(reg.getLabel())
            
            item = QtGui.QTableWidgetItem(str(reg.get()))
            item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.registerTable.setItem(count, 0, item)
 
            item = QtGui.QTableWidgetItem(libproc.ltoh(reg.get(), reg.getSize()))
            item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.registerTable.setItem(count, 1, item)
            count += 1
            
    def updateRegister(self, reg):
        value = reg.get()
        size = reg.getSize()
        self.registerTable.item(reg.getRank(), 0).setText(str(value))
        self.registerTable.item(reg.getRank(), 0).setBackground(QtGui.QColor(0,160,0))
        self.registerTable.item(reg.getRank(), 1).setText(libproc.ltoh(value, size))
        self.registerTable.item(reg.getRank(), 1).setBackground(QtGui.QColor(0,160,0))

       
    def cleanRegisterMarker(self):
        for row in range(self.registerTable.rowCount()):
            for col in range(self.registerTable.columnCount()):
                self.registerTable.item(row, col).setBackground(QtGui.QColor(255,255,255))
                
    #
    # INDICATOR 
    #    
    
    def displayIndicator(self, board):
        indicatorList = board.chip.getIndicatorList()
        #self.indicatorTable.setRowCount(len(indicatorList))
        self.indicatorTable.setRowCount(1)

        colWidth = 50

        width = (colWidth +5) * len(indicatorList)
        height = 60

        self.indicatorTable.setMinimumSize(QtCore.QSize(width, height))
        self.indicatorTable.setMaximumSize(QtCore.QSize(width, height))

        self.indicatorTable.setColumnCount(len(indicatorList))

        nameList = []
        for indicator in indicatorList:
            nameList.append(indicator.getName())
        self.indicatorTable.setHorizontalHeaderLabels(nameList)
        
        for i in range(len(indicatorList)):
            self.indicatorTable.horizontalHeader().resizeSection(i, colWidth)

        count = 0
        for indicator in indicatorList:
            self.indicatorTable.horizontalHeaderItem(count).setToolTip(indicator.getLabel())
            self.indicatorTable.setColumnWidth(count,  colWidth)
            item = QtGui.QTableWidgetItem(str(indicator.get()))
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.indicatorTable.setItem(0, count, item)
            count += 1
 
    def updateIndicator(self, indicator):
        value = indicator.get()
        self.indicatorTable.item(0, indicator.getRank()).setText(str(value))
        self.indicatorTable.item(0, indicator.getRank()).setBackground(QtGui.QColor(0,160,0))
   
                
    def cleanIndicatorMarker(self):
        for col in range(self.indicatorTable.columnCount()):
            self.indicatorTable.item(0, col).setBackground(QtGui.QColor(255,255,255))
