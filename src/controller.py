# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#

import os
import imp
import sys

from error import Error
from config import Config

class Controller:
    
    __name    = 0
    __address = 1
    __size    = 2
    __fct     = 3
    
    def __init__(self, display):
        self.display= display
        "initialize all device management structure"
        # list of all device modules:
        # - created by parsing list of device_xxx.py files in hardware/device
        # - stores references to imported modules
        self.deviceModuleList = []
        # list of used devices for the selected board
        self.connectedDeviceList = []
        # list of handlers to process when memory is updated
        self.connectedHanderList = []
        # used to assign a rank to each created device
        # useful to differentiate device when severals of same type are created
        # also used to shift UI in order to prevent windows to cover each other
        self.deviceRank = 0

        
    def delete(self):
        for device in self.connectedDeviceList:
            device.deleteDevice()
        
    def loadDeviceList(self):
        "- Load the list of devices defined in hardware/device"
        "- Import module for each one"
        self.deviceModuleList = []
        deviceDir = Config.getDeviceDir()
        for fileName in os.listdir(deviceDir):
            # only file with device_xxx.py must be considered
            if fileName[0:7] == "device_" and fileName[-3:] == ".py":
                deviceName = fileName[7:-3]
                # retrieve full path name
                fullPath = os.path.join(deviceDir, fileName)
                # import module and add it to module list
                module = imp.load_source(deviceName, fullPath)
                self.deviceModuleList.append(module)
                
    def createDevice(self, deviceDef):
        "Associate a device to a board"
        "- for each existing device module, check if device name matches"
        "- call its corresponding device creation function"
        deviceName = deviceDef[0]
        for module in self.deviceModuleList:
            # check device name
            if deviceName == module.getDeviceName():
                self.connectedDeviceList.append(module.createDevice(self, self.deviceRank, deviceDef, self.display))
                self.deviceRank += 1
                return
        raise Error(Error.error, "device " + deviceName + " doesn't exist")
                                                     
    def declareInput(self, name, address, size, fct):
        "Call by each device during its initialization "
        "- Defines memory address used by device to get input"
        "- Device handler will be called when a change will occur to this address"
        
        self.connectedHanderList.append([name, address, size, fct])
        
    def callInput(self, memory, address, size):
        "Call each device handler declaring a specific memory area as its input"
        
        for device in self.connectedHanderList:          
            impacted = False      
            # check if the device is impacted by memory update
            for i in range(size):
                if device[Controller.__address] <= address + i < (device[Controller.__address] + device[Controller.__size]):
                    impacted = True
                    break
            
            if impacted:
            # create a buffer to communicate with the device
            # Note that changed memory area could not match exactly
            # input area boundaries then initialize a buffer with required memory content
                data = bytearray([])
                for i in range(device[Controller.__size]):
                    value = memory.getByte(device[Controller.__address] + i)
                    data.append(value)
                device[Controller.__fct](device[Controller.__address], device[Controller.__size], data)