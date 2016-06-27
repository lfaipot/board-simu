# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#

import libproc
from error import Error
from processor import Processor, Register, Indicator

class Chip(Processor):
    
    __hexaChar        = ''
    __decChar         = ''

    
    def __init__(self):
        super(Chip, self).__init__("edu1")
        
        addressSize     = 1
        regSize         = 1
        instructionSize = 1
        wordSize        = 1
        
   
        patternLabel    = "[a-zA-Z]+[a-zA-Z0-9]*"
        patternDec      = "[0-9]+"
        patternData     = "([0-9]+)"
    
        self.PC    = self.addRegister('PC', "Program Counter", Register.PC, Register.StatusN, Register.UnsignedInteger, regSize)
        self.regA  = self.addRegister('A', "A Register", Register.Acc, Register.StatusY, Register.SignedInteger, regSize)
        self.regB  = self.addRegister('B', "B Register", Register.Acc, Register.StatusN, Register.SignedInteger, regSize)
        
        self.zero       = self.addIndicator('Z', "Zero", Indicator.Zero)
    

        # reg definition must be first to avoid A or B to match with Label pattern
        self.regref    = self.addAddressingMode('reg', "([AB])", 1, self.decodeReg)
        self.absolute  = self.addAddressingMode('absolute', "(" + patternDec + ")|(" + patternLabel + ")" , addressSize, self.decodeInt)
        self.immediate = self.addAddressingMode('immediate', "#(-?\d*)", wordSize, self.decodeInt)
            
        self.addInstruction(0x01, 'LDA', self.lda, self.absolute)
        self.addInstruction(0X02, 'LDB', self.ldb, self.absolute)
        self.addInstruction(0x03, 'STA', self.sta, self.absolute)
        self.addInstruction(0x04, 'STB', self.stb, self.absolute)
        self.addInstruction(0x05, 'ADD', self.add, self.regref)
        self.addInstruction(0x06, 'DEC', self.dec, self.regref)
        self.addInstruction(0x07, 'MOVA', self.mova, self.immediate)
        self.addInstruction(0x08, 'MOVB', self.movb, self.immediate)
        self.addInstruction(0x09, 'JMP', self.jmp, self.absolute)
        self.addInstruction(0x0a, 'JMPZ', self.jmpz, self.absolute)
        self.addInstruction(0xff, '.END', self.end, None)
        
        self.addData(patternData, wordSize, self.decodeInt)
        
        self.defineLabelPattern(patternLabel)
        
        self.addSection(".DATA", True, None)
        self.addSection(".CODE", False, self.decodeAddr)
        
        self.setDataWithAddress(True)
        self.setWordSize(wordSize)
        self.setAddressSize(addressSize)
        self.setInstructionSize(instructionSize)
        self.setComment(';')
        
    def decodeInt(self, string):
        try:
            hexa = False
            if (len(self.__hexaChar) > 0):
                if string[0] == self.__hexaChar:
                    string = string[1:]
                    hexa = True
                else:
                    hexa = False
            elif (len(self.__decChar) > 0):
                if string[0] == self.__decChar:
                    string = string[1:]
                    hexa = False
                else:
                    hexa = True

            if (hexa):
                value = int(string, 16)
            else:
                value = int(string)
            return value
        except:
            raise Error(Error.error, "Invalid numeric syntax")
            return 0    
        
    def decodeAddr(self, string):
        return self.decodeInt(string)
    
    def decodeReg(self, string):
        if string == 'A':
            return 0
        return 1
    
    #
    # implementation of callback functions
    #
    def lda(self, board, operandList):
        address = operandList[0].getValue()
        self.regA.set(board.memory.get(address, self.regA.getSize()))
        
    def ldb(self, board, operandList):
        address = operandList[0].getValue()
        self.regB.set(board.memory.get(address, self.regB.getSize()))
        
    def sta(self, board, operandList):
        address = operandList[0].getValue()
        board.memory.set(address, self.regA.getSize(), self.regA.get())
    
    def stb(self, board, operandList):
        address = operandList[0].getValue()
        board.memory.set(address, self.regB.getSize(), self.regB.get())
        
    def mova(self, board, operandList):
        value = operandList[0].getValue()
        self.regA.set(value)
        
    def movb(self, board, operandList):
        value = operandList[0].getValue()
        self.regB.set(value)
    
    def add(self, board, operandList):
        reg = operandList[0].getValue()
        value = self.regA.get() + self.regB.get()
        if reg == 0:
            reg = self.regA
        else:
            reg = self.regB
        reg.set(value)
    
    def dec(self, board, operandList):
        reg = operandList[0].getValue()
        if reg == 0:
            reg = self.regA
        else:
            reg = self.regB
        reg.set(reg.get() - 1)
            
    def jmp(self, board, operandList):
        address = operandList[0].getValue()
        self.PC.set(libproc.ltoui(address, self.PC.getSize()))
    
    def jmpz(self, board, operandList):
        address = operandList[0].getValue()
        if (self.regA.get() == 0):
            self.PC.set(libproc.ltoui(address, self.PC.getSize()))
            
    def end(self, board, operand):
        self.setEndProgram(True)
