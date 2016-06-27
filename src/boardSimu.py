# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#

import sys
import os
#import gc

from PyQt4 import QtGui, QtCore
from functools import partial

from boardSimuUi import Ui_BoardSimuMain

from boardMgr import BoardMgr
from config import Config
from board import Board

import helpMgr

ProgramVersion = "1.0"

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class BoardSimu(QtGui.QMainWindow, Ui_BoardSimuMain):
    def __init__(self, parent=None):
        super(BoardSimu, self).__init__(parent)
        self.setupUi(self)
        self.config = Config("boardsimu.cfg") 
        
        self.defineActions()
        self.boardMgr = None
        self.fileName = None
        self.programChanged = False

        
        x = self.config.getOption("MAIN WINDOW", "X")
        y = self.config.getOption("MAIN WINDOW", "Y")
        window = self.geometry()

        valX = window.x()
        if x != "":
            valX = int(x)
        valY = window.y()
        if y != "":
            valY = int(y)
        self.setGeometry(QtCore.QRect(valX, valY, window.width(), window.height()))

        self.show()
        
        defaultBoard = self.config.getOption("DEFAULT BOARD", "name")
        if (defaultBoard != ""):
            # check if the board, selected during the previous usage, still exists
            found = False
            boardList = Board.getList()
            for boardDesc in boardList:
                if defaultBoard == boardDesc[0]:
                    found = True
                    boardLabel = boardDesc[1]
                    self.openBoard(defaultBoard, boardLabel)
            if not found:
                # remove value
                self.config.setOption("DEFAULT BOARD", "name", "")
                
        self.errorEdit.setMaximumSize(QtCore.QSize(1000, 150))
            
            
        #self.programEdit.setStyleSheet('font-size: 12pt; font-family: Courier;')
            
        #gc.set_debug(gc.DEBUG_STATS)
                
    def defineActions(self):
        # look for available board
        
        boardList = Board.getList()
        self.actionBoard = []
        for boardDesc in boardList:
            action = QtGui.QAction(self)
            boardName = boardDesc[0]
            boardLabel = boardDesc[1]
            action.setObjectName(_fromUtf8("action" + boardName))
            f = partial(self.openBoard, boardName, boardLabel)
            action.triggered.connect(f)
            action.setText(QtGui.QApplication.translate("MainWindow", boardLabel, None, QtGui.QApplication.UnicodeUTF8))
            self.menuBoard.addAction(action)
            self.actionBoard.append(action)
        
        self.actionQuit.triggered.connect(self.quit)
        self.actionNew.triggered.connect(self.newFile)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(self.saveFile)
        self.actionSaveAs.triggered.connect(self.saveAsFile)
        self.actionAbout.triggered.connect(self.displayAbout)
        self.actionReleaseNotes.triggered.connect(self.displayReleaseNotes)
        QtCore.QObject.connect(self.loadButton, QtCore.SIGNAL('clicked()'), self.loadProgram)
        QtCore.QObject.connect(self.programEdit, QtCore.SIGNAL('textChanged()'), self.textChanged)
        self.setMouseTracking(True)
        self.centralwidget.setMouseTracking(True)
        
        self.actionNew.setEnabled(True)
        self.actionSave.setEnabled(False)
        self.actionSaveAs.setEnabled(False)
        self.loadButton.setEnabled(False)
        self.actionReleaseNotes.setEnabled(True)
        self.actionAboutProcessor.setEnabled(False)
        self.actionAboutBoard.setEnabled(False)
        
    #
    # Predefined Windows Management functions
    #
    def moveEvent(self, oldPos):
        """Triggered when window is moved
        Saves new window position. Window ill be re-created at this position.
        """
        
        self.config.setOption("MAIN WINDOW", "X", str(self.x()))
        self.config.setOption("MAIN WINDOW", "Y", str(self.y()))
        self.config.write()
        
    def closeEvent(self, event):
        self.quit()
    
    #
    # particular event processing
    #
    def textChanged(self):
        """Triggered when program text is changed.
        Sets menu accordingly and note that saving changes is required.
        """
        
        self.programChanged = True
        if self.fileName:
            self.actionSave.setEnabled(True)
        self.actionSaveAs.setEnabled(True)
                
    def quit(self):
        if (self.programChanged):
            if not self.checkProgramSave():
                return
        QtGui.qApp.quit()
        sys.exit(0)
           
    def displayAbout(self):
        QtGui.QMessageBox.about(self, "Board Simulator", 
                                self.tr(u"Version " + ProgramVersion + "\n" +
                                u"\n" +
                                u"Author\n" +
                                u"    Laurent Faipot (Laurent.Faipot@free.fr)\n" +
                                u"\n" +
                                u"Tester and early adopter for education\n" +
                                u"    Sylvaine Chambre (Sylvaine.Chambre@free.fr)\n")
                                )
        
    def displayReleaseNotes(self):
        docDir = Config.getDocDir()
        releaseFile = os.path.join(docDir, "release_notes.html")
        helpMgr.display(releaseFile)
    
    
    #
    # BOARD
    #
    
    def openBoard(self, boardName, boardLabel):
        """Creates board window
        """
        
        if (self.boardMgr):
            # already a board displayed: delete it
            self.boardMgr.delete()
        self.config.setOption("DEFAULT BOARD", "name", boardName)
        self.boardMgr = BoardMgr(boardName, boardLabel, app, self)
        self.loadButton.setEnabled(True)
            
    #
    # PROGRAM FILE
    #        
    
    def openFile(self):
        """Opens Program file and stores it into program edition widget
        Also updates list of recently opened files
        """
        
        self.checkProgramSave()
        lastOpenedFile = self.config.getLastOpenedFile()
        if (lastOpenedFile == ""):
            lastOpenedFile = QtCore.QDir.homePath()
        fileName = QtGui.QFileDialog.getOpenFileName(
                        self,
                        "Open program file",
                        lastOpenedFile,
                        "Assembly files (*.ass *.txt);;All files (*.*)"
                        )
            
        if fileName:
            self.fileName = fileName
            self.config.setRecentFiles(self.fileName)
            self.loadFile(self.fileName)
            self.actionSaveAs.setEnabled(True)
            currentFile = os.path.basename(str(fileName))
            self.setWindowTitle(currentFile + " - BoardSimu Editor")
            self.clearErrors()
    
    def newFile(self):
        """Cleans everything, including saving current program, before writing a new one
        """
        
        self.checkProgramSave()
        self.programEdit.clear()
        self.fileName = None
        self.programChanged = False
        self.actionSave.setEnabled(False)
        self.setWindowTitle("New - BoardSimu Editor")
             
    def saveFile(self):
        """Saves current program into its original file
        """
        
        self.writeFile()
        self.actionSave.setEnabled(False)
         
    def saveAsFile(self):
        """Saves current program into a new file
        """
        
        if not self.fileName:
            fileName = ""
        else:
            fileName = self.fileName
        fileName = QtGui.QFileDialog.getSaveFileName(None, 'Save File',
                                             fileName)
        if fileName:
            self.fileName = fileName
            self.saveFile()
            return True
        else:
            return False
        
    def writeFile(self):
        """Saves program into a file and updates recent opened files list
        """
        
        filedata = self.programEdit.toPlainText()
        f = open(self.fileName, "w")
        f.write(filedata)
        f.close()
        self.programChanged = False
        # change file name into title
        currentFile = os.path.basename(str(self.fileName))
        self.setWindowTitle(currentFile + " - BoardSimu Editor")
        # change default file into configuration
        self.config.setRecentFiles(self.fileName)
        
    
    def loadFile(self, fileName):
        """Loads file into text edition widget.
        filename: name of file to load
        """
        
        text = open(fileName).read()
        self.programEdit.setPlainText(text)
        self.programChanged= False
        self.actionSave.setEnabled(False)
             
    def checkProgramSave(self):
        if (not self.programChanged):
            return True
        answer = QtGui.QMessageBox.question(self, 
                                       self.tr(u"Quit"), 
                                       self.tr(u"Your program has been modified. Do you want to save it?"), 
                                       QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if (answer == QtGui.QMessageBox.Yes):
            return self.saveAsFile()
        return True
    
    #
    # PROGRAM
    #        
    
    def loadProgram(self):
        """Stores program into a temporary file and passes its name to analyzer.
        Using a file to communicate with analyzer is for future use like executing without using GUI
        (for automated testing for instance)
        """
        
        self.clearErrors()
        tmpFile = QtCore.QTemporaryFile()
        tmpFile.open()
        fileData = self.programEdit.toPlainText()
        tmpFile.writeData(fileData)
        tmpFile.close()
        if not self.boardMgr.processFile(tmpFile.fileName()):
            self.displayErrors()
        
    def displayErrors(self):
        """Display program analysis errors:
        - error messages into error widget
        - change color of lines with errors into program text
        """
        
        # highlight lines with errors to ease visibility
        errors = []
        for inst in self.boardMgr.board.program.getProgram():
            if len(inst.getErrorList()) > 0:
                selection = QtGui.QTextEdit.ExtraSelection()
                programEdit = self.programEdit
                programEdit.moveCursor(QtGui.QTextCursor.Start)
                for _ in range(inst.getLineNb() - 1):
                        programEdit.moveCursor(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor)
                lineColor = QtGui.QColor(255,0,0)
                selection.format.setBackground(lineColor)
                selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
                selection.cursor = self.programEdit.textCursor()
                errors.append(selection)
        self.programEdit.setExtraSelections(errors)
        
        # display errors in specific widget
        text = ""
        for inst in self.boardMgr.board.program.getProgram():
            if len(inst.getErrorList()) > 0:
                # build text for each error line: add line number for the 1st one
                line = '<{:4d}>'.format(inst.getLineNb())
                for error in inst.getErrorList():
                    line += " " + error
                    if text != "":
                        text += "\n"
                    text += line
                    line = '{:4s}'.format("")
        self.errorEdit.setPlainText(text)
        
    def clearErrors(self):
        """Reset all errors before starting a new program analysis
        """
        
        self.programEdit.setExtraSelections([])
        self.errorEdit.setPlainText("")

if __name__ == '__main__': 
    app = QtGui.QApplication(sys.argv)
    globalDisplay = BoardSimu()
    sys.exit(app.exec_())
