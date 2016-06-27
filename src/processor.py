# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#

import libproc
import trace
from error import *

#
# EXEC ERROR Exception
#
#    raise during execution to process error
#
class ExecError(Error):
    def __init__(self, severity, msg):
        Error.__init__(self, severity)
        self.msg = msg
        
    def __str__(self):
        return self.msg
    
class AddressingMode:
    
    def __init__(self, name, pattern, size, processing):
        # name of the addressing mode
        self.__name       = name
        # pattern used to check addressing mode 
        self.__pattern    = pattern
        # size of operand coding
        self.__size       = size
        # function call to convert operand
        self.__processing =   processing
    
    def __str__(self):
        return self.__name
    
    def getPattern(self):
        return self.__pattern
    
    def getSize(self):
        return self.__size
    
    def getProcessing(self):
        return self.__processing

#
# SECTION Management
#

class Section:
    
    def __init__(self, name, isData, fct):
        self.__name     = name
        self.__isData   = isData
        self.__fct      = fct
        
    def __str__(self):
        return self.__name
        
    def getName(self):
        return self.__name
    
    def isData(self):
        return self.__isData
        
    def getFct(self):
        return self.__fct
#
# INSTRUCTION Management
#
class Instruction:
        
    def __init__(self, opcode, mnemonic, callback, addressingMode, isOffset= False):
        self.__opcode     = opcode
        self.__mnemonic   = mnemonic
        self.__callback   = callback
        self.__addressing = addressingMode
        self.__isOffset   = isOffset
        
    def __str__(self):
        return self.__mnemonic
    
    def getOpcode(self):
        return self.__opcode
    
    def getMnemonic(self):
        return self.__mnemonic
    
    def getCallback(self):
        return self.__callback
    
    def getAddressing(self):
        # "program" has been designed to support several addressing mode
        # per opcode
        # not implemented yet on instruction definition but a list is returned
        if self.__addressing:
            return [self.__addressing]
        else:
            return []
        
    def isOffset(self):
        return self.__isOffset
    
class Data:
    
    def __init__(self, mnemonic, size, fct):
        self.__mnemonic =   mnemonic
        self.__size     =   size
        self.__fct      = fct
        
    def __str__(self):
        return self.__mnemonic

    def getMnemonic(self):
        return self.__mnemonic
    
    def getSize(self):
        return self.__size
    
    def getFct(self):
        return self.__fct
        
class Parameter:
    
    def __init__(self, addressing, value, size):
        self.__addressing = addressing
        self.__value      = value
        self.__size       = size
        
    def getAddressing(self):
        return self.__addressing
    
    def getValue(self):
        return self.__value
    
    def getSize(self):
        return self.__size
    
#
# INDICATOR management
#
#    like Carry, Overflow, Zero and others
#

class Indicator:
    
    Carry       = 1
    Zero        = 2
    Overflow    = 3
    Negative    = 4
    Other       = 5
    
    # class attribute: it used to get a unique rank
    __rank      = 0

    # class attribute because used before instance creation
    # and common to all indicators
    # function to call when an indicator value is changed
    __displayChange = None
    
    @classmethod
    def reset(self):
        Indicator.__rank = 0
        
    @classmethod
    def whenUpdated(cls, fct):
        cls.__displayChange = fct
        
    def __init__(self, processor, name, label, indicatorType, rank=None):
        self.__processor = processor
        self.__name = name
        self.__label = label
        self.__indicatorType = indicatorType
        self.__value = 0
        if (rank):
            self.__rank = rank
        else:    
            self.__rank = Indicator.__rank
        Indicator.__rank += 1
    
    def getName(self):
        return self.__name
    
    def getLabel(self):
        return self.__label
    
    def getRank(self):
        return self.__rank
    
    def getType(self):
        return self.__indicatorType
    
    def get(self):
        return self.__value
    
    def set(self, value):
        if (value != self.__value):
            self.__value = value
            for reg in self.__processor.getRegisterList():
                if (reg.getType() == Register.Status):
                    if (value == 1):
                        mask = 1 << self.__rank
                        reg.set(reg.get() | mask)
                    else:
                        mask = ~(1 << self.__rank)
                        reg.set(reg.get() & mask)
                    
            if (Indicator.__displayChange):
                Indicator.__displayChange(self)

#
# REGISTER management
#
#     like integer and index register
#
class Register:
    
    PC                  = 1
    SP                  = 2
    Index               = 3
    Acc                 = 4
    Status              = 5
    
    # StatusY: when the register content is updated, indicators are updated accordingly
    StatusN             = 1
    StatusY             = 2
    
    SignedInteger       = 1
    UnsignedInteger     = 2
    Float               = 3 # not supported yet

    __displayChange       = None
    __rank = 0
    
    def __init__(self, processor, name, label, regType, status, frmt, size):
        self.__processor = processor
        self.__name   = name
        self.__label  = label
        self.__regType = regType
        self.__status = status
        self.__format = frmt
        self.__value  = 0
        self.__size   = size
        self.__min    = 0
        self.__max    = 0
        if (format == Register.SignedInteger):
            self.__min  = - (2 ** (size * 8 - 1))
            self.__max  = 2 ** (size * 8 - 1) -1
        elif (format == Register.UnsignedInteger):
            self.__min  = 0
            self.__max  = 2 ** (size * 8) - 1
        self.__rank = Register.__rank
        Register.__rank += 1
    
    @classmethod
    def reset(self):
        Register.__rank = 0
    
    @classmethod    
    def whenUpdated(cls, fct):
        cls.__displayChange = fct
       
    def set(self, value):           
        # convert value in sized integer
        val = value
        if (self.__format == Register.SignedInteger):
            value = libproc.ltoi(value, self.__size)
        elif (self.__format == Register.UnsignedInteger):
            value = libproc.ltoui(value, self.__size)

        self.__value = value
        if (Register.__displayChange):
            Register.__displayChange(self)
        if (self.__status == Register.StatusY):
            self.__processor.setZero(value)
            self.__processor.setNeg(value)

    def get(self):
        return self.__value  
                
    def getName(self):
        return self.__name
    
    def getLabel(self):
        return self.__label
    
    def getRank(self):
        return self.__rank
    
    def getSize(self):
        return self.__size
    
    def getType(self):
        return self.__regType


class Processor(object):
    
    __displayChange = None
    
                
    @classmethod
    def whenUpdated(cls, fct):
        cls.__displayChange = fct
        
    def __init__(self, name):
        self.__name             = name
        self.__loadAddress      = 0
        self.__regList          = []
        self.__indicatorList    = []
        self.__endProgram       = False
        self.__instructionSet   = []
        self.__instructionOpcode = {}
        self.__addressingSet    = []
        self.__dataSet          = []
        self.__sectionSet       = []
        self.__dataWithAddress  =   False
        self.__wordSize         = 0
        self.__addressSize      = 0
        self.__instructionSize  = 0
        self.__operandSep       = ''
        self.__helpFile         = ""
        Register.reset()
        Indicator.reset()
        
    #
    # REGISTER management
    #
        
    def addRegister(self, name, label, regType, status, format, size):
        reg = Register(self, name, label, regType, status, format, size)
        self.__regList.append(reg)
        return reg
    
        
    def getRegisterList(self):
        return self.__regList
    
    #
    # INDICATOR management
    #
    
    def addIndicator(self, name, label, indicatorType, rank=None):
        indicator = Indicator(self, name, label, indicatorType, rank)
        self.__indicatorList.append(indicator)
        return indicator
        
    def getIndicatorList(self):
        return self.__indicatorList
    
    def setIndic(self, indicType, value):
        for ind in self.__indicatorList:
            if ind.getType() == indicType:
                ind.set(value)
 
    def setZero(self, value):
        if (value == 0):
            self.setIndic(Indicator.Zero, 1)
        else:
            self.setIndic(Indicator.Zero, 0)
                    
    def setNeg(self, value):
        if (value < 0):
            self.setIndic(Indicator.Negative, 1)
        else:
            self.setIndic(Indicator.Negative, 0)
                    
    def setOverflow(self, value):
        self.setIndic(Indicator.Overflow, value)
                
    def setCarry(self, value):
        self.setIndic(Indicator.Carry, value)
 
    def clearIndicator(self):
        for ind in self.__indicatorList:
            ind.set(0)
    
    #
    # DATA definition management
    #
    def addData(self, mnemonic, size, fct):
        data = Data(mnemonic, size, fct)
        self.__dataSet.append(data)
        return data
     
    def getDataSet(self):
        return self.__dataSet

    
    #
    # INSTRUCTION management
    #
    def addInstruction(self, opcode, mnemonic, callback, addressingMode, isOffset = False):
        inst = Instruction(opcode, mnemonic, callback, addressingMode, isOffset)
        #self.instructionSet[opcode] = inst
        self.__instructionSet.append(inst)
        self.__instructionOpcode[opcode] = inst
        return inst
                                   
    def getInstructionSet(self):
        trace.debug(4, "PROCESSOR getInstructionSet")
        l = []
        for inst in self.__instructionSet:
            l.append(inst)
        return l
    
    def lookForInstruction(self, opcode):
        try:
            return self.__instructionOpcode[opcode]
        except:
            return None
        
        
    #
    # ADDRESSING MODE management
    #
    def addAddressingMode(self, name, pattern, size, processing):
        addressing = AddressingMode(name, pattern, size, processing)
        self.__addressingSet.append(addressing)
        return addressing
        
    def getAddressingSet(self):
        l = []
        for mode in self.__addressingSet:
            l.append(mode)
        return l
    
    def defineLabelPattern(self, pattern):
        self.__labelPattern = pattern
        
    def getLabelPattern(self):
        return self.__labelPattern
    
    def addSection(self, name, isData, fct):
        section = Section(name, isData, fct)
        self.__sectionSet.append(section)

    def getSectionSet(self):
        trace.debug(4, "PROCESSOR getSectionSet")
        return self.__sectionSet
    
    def isData(self):
        return self.isData
    
    def setDataWithAddress(self, value):
        self.__dataWithAddress = value
        
    def isDataWithAddress(self):
        return self.__dataWithAddress
    
    def setOperandSeparator(self, value):
        self.__operandSep = value
    
    def getOperandSeparator(self):
        return self.__operandSep
    
    def setComment(self, value):
        self.__commentChar = value
        
    def getComment(self):
        return self.__commentChar
    
    def setAddressSize(self, value):
        self.__addressSize = value
        
    def getAddressSize(self):
        return self.__addressSize

    def setInstructionSize(self, value):
        self.__instructionSize = value
        
    def getInstructionSize(self):
        return self.__instructionSize
    
    def setWordSize(self, value):
        self.__wordSize = value
    
    def getWordSize(self):
        return self.__wordSize
    
    def setEndProgram(self, value):
        self.__endProgram = value
        
    def executeNext(self, board):
        memory = board.memory
        if (self.__displayChange):
            self.__displayChange(self.PC.get())
        address = self.PC.get()
        
        opcode = libproc.ltoui(memory.get(address, self.__instructionSize), self.__instructionSize)
        self.PC.set(self.PC.get() + self.__instructionSize)

        # check opcode
        inst = self.lookForInstruction(opcode)
        if (not inst):
            raise ExecError(Error.error, "Address: " + str(hex(address)) + ": invalid opcode " + str(hex(opcode)))
            return True
        
        parameterList = []
        for addressing in inst.getAddressing():
            size = addressing.getSize()
            value = memory.get(self.PC.get(), size)
            self.PC.set(self.PC.get() + size)
            parameter = Parameter(addressing, value, size)
            parameterList.append(parameter)

        #self.instructionSet[opcode][self.InstFct](self, board, parameterList)
        callback = inst.getCallback()
        if callback:
            callback(board, parameterList)
        return self.__endProgram
    
    def clear(self):
        for reg in self.__regList:
            reg.set(0)
        for indic in self.__indicatorList:
            indic.set(0)
        