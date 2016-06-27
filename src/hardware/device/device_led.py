# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#
#
# LED emulation
#
#    parameter in board description file
#        - device name: "Led display"
#        - number of leds: can be greater than word size (ex: 16 leds on 8-bit architecture)
#        - input address: address to be used for setting led value
#

import os
from PyQt4 import QtGui

import libproc
from ledUI import Ui_ledWidget
from controller import *


def getDeviceName():
    return "Led display"

def createDevice(controller, rank, paramList, parent):
    return Led(controller, rank, paramList, parent)

class Led(QtGui.QMainWindow, Ui_ledWidget):
    
    def __init__(self, controller, rank, paramList, parent):
        super(Led, self).__init__(parent)
        self.setupUi(self)
        self.controller = controller
        self.rank   = rank
        self.paramList = paramList
        self.nbLeds = int(paramList[1])
        self.inputAddr = int(paramList[2])
        self.parent = parent
        
        self.setupUi(self)
        
        devicePath = os.path.dirname(os.path.abspath(__file__))
        self.onFile = os.path.join(devicePath, "yellow-on-32.png")
        self.offFile = os.path.join(devicePath, "yellow-off-32.png")

        # declare itself to Board controller
        self.controller.declareInput("LED", self.inputAddr, self.nbLeds / 8, self.changeInput)
        
        self.decAddr.setText(str(self.inputAddr))
        self.hexaAddr.setText("x" + libproc.ltoh(self.inputAddr, 2))
        self.decValue.setText("")
        self.hexaValue.setText("")
 
        self.led = []
        startX = 40
        sizeLed = 32
        filler = 10
        for i in range(self.nbLeds):
            led = QtGui.QLabel(self)
            led.setGeometry(startX + ((self.nbLeds - 1 - i) * (sizeLed + filler)), 10, 400, 100)
            # use full ABSOLUTE path to the image, not relative
            led.setPixmap(QtGui.QPixmap(self.offFile))
            led.show()
            self.led.append(led)
        self.resize((sizeLed + filler) * self.nbLeds + 80 ,120)
        
        screen = QtGui.QDesktopWidget().screenGeometry()
        window = self.geometry()
        # move window based on its rank to get it visible if other devices have been displayed
        self.move((screen.width() - window.width())/2 + (self.rank * 40), 
                  (screen.height() - window.height())/2 + self.rank * 40)
        
        self.show()
        
    def closeEvent(self, event):
        self.parent.quit()
    
    def deleteDevice(self):
        self.deleteLater()
        
    def changeInput(self, address, size, data):
        "Set on or off leds depending on value of corresponding bit"
        value = 0
        for i in range(size):
            value = value * 256 + data[i]
        self.decValue.setText(libproc.ltoa(value, size))
        self.hexaValue.setText("x" + libproc.ltoh(value, size))
        
        for bit in range(size * 8):
            # process per byte
            # remember: max..0 so 
            # . byte 0: max ..
            # . byte n: ..0 
            noByte = size - (bit // 8) - 1
            value = data[noByte]
            mask = 1 << (bit % 8)
            # leds are numbered right to left: max ..0
            # so byte 0 is max.. and byte n is ..0
            noLed = bit
            if (value & mask):
                self.led[noLed].setPixmap(QtGui.QPixmap(self.onFile))
            else:
                self.led[noLed].setPixmap(QtGui.QPixmap(self.offFile))
        self.show()