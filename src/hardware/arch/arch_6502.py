# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#
import re
import libproc
from error import Error
from processor import Processor, Register, Indicator, Parameter, ExecError
from program import ProgramError


class Chip(Processor):

    __hexaChar        = '$'
    __decChar         = ''

    
    def __init__(self):
        super(Chip, self).__init__("6502")
        
        wordSize        = 1
        addressSize     = 2
        instructionSize = 1
        
        # size of offset value on branch
        offsetSize      = 1
        
        # 1 or 2 hexa digits starting with $ 
        patternByte  = "\$[0-9a-fA-F]{1,2}"
        # 3 or 4 hexa digits starting with $
        patternWord  = "\$[0-9a-fA-F]{4}"
        # string starting with a letter and including letter, digit and under score
        patternLabel    = "[a-zA-Z]+[a-zA-Z0-9]*"
    
        self.PC    = self.addRegister('PC', "Program Counter", Register.PC, Register.StatusN, Register.UnsignedInteger, addressSize)
        self.SP    = self.addRegister('SP', "Stack Pointer", Register.SP, Register.StatusN, Register.UnsignedInteger, addressSize)
        self.regA  = self.addRegister('A', "Accumulator", Register.Acc, Register.StatusY, Register.SignedInteger, wordSize)
        self.regX  = self.addRegister('X', "X Index", Register.Index, Register.StatusY, Register.SignedInteger, wordSize)
        self.regY  = self.addRegister('Y', "Y index", Register.Index, Register.StatusY, Register.SignedInteger, wordSize)
        self.PSR   = self.addRegister('PSR', "Program Status Register", Register.Status, Register.StatusN, Register.UnsignedInteger, wordSize)
        
        self.carry      = self.addIndicator('C', "Carry", Indicator.Carry, 0)
        self.zero       = self.addIndicator('Z', "Zero", Indicator.Zero, 1)
        self.interrupt  = self.addIndicator('I', "Interrupt", Indicator.Other, 2)
        self.decimal    = self.addIndicator('D', "Decimal", Indicator.Other, 3)
        self.brkInd      = self.addIndicator('B', "Break", Indicator.Other, 4)
        # 5: reserved for future use
        self.reserved   = self.addIndicator('-', "Reserved", Indicator.Other, 5)
        self.overflow   = self.addIndicator('V', "Overflow", Indicator.Overflow, 6)
        self.negative   = self.addIndicator('N', "negative", Indicator.Negative, 7)
               
        self.accumulator = self.addAddressingMode('accumulator', "(A)", 0, self.decodeReg)
        self.immediate   = self.addAddressingMode('immediate', "#(" + patternByte + ")", wordSize, self.decodeInt)
        self.zeroPage    = self.addAddressingMode('zeroPage', "(" + patternByte + ")", offsetSize, self.decodeInt)
        self.zeroPageX   = self.addAddressingMode('zeroPageX', "(" + patternByte + "),X", offsetSize, self.decodeInt)
        self.zeroPageY   = self.addAddressingMode('zeroPageY', "(" + patternByte + "),Y", offsetSize, self.decodeInt)
        self.absolute    = self.addAddressingMode('absolute', "(" + patternWord + ")|(" + patternLabel + ")" , addressSize, self.decodeInt)
        self.absoluteX   = self.addAddressingMode('absoluteX', "(" + patternWord + "),X|(" + patternLabel + "),X", addressSize, self.decodeInt)
        self.absoluteY   = self.addAddressingMode('absoluteY', "(" + patternWord + "),Y|(" + patternLabel + "),Y", addressSize, self.decodeInt)
        self.indirect    = self.addAddressingMode('indirect', "\((" + patternWord + ")\)|\((" + patternLabel + ")\)", addressSize, self.decodeInt)
        self.indirectX   = self.addAddressingMode('indirectX', "\((" + patternByte + "),X\)|\((" + patternLabel + "),X\)", offsetSize, self.decodeInt)
        self.indirectY   = self.addAddressingMode('indirectY', "\((" + patternByte + ")\),Y|\((" + patternLabel + ")\),Y", offsetSize, self.decodeInt)
                             
        self.addInstruction(0x69, "ADC", self.adc, self.immediate)
        self.addInstruction(0x65, "ADC", self.adc, self.zeroPage)
        self.addInstruction(0x75, "ADC", self.adc, self.zeroPageX)
        self.addInstruction(0x6d, "ADC", self.adc, self.absolute)
        self.addInstruction(0x7d, "ADC", self.adc, self.absoluteX)
        self.addInstruction(0x79, "ADC", self.adc, self.absoluteY)
        self.addInstruction(0x61, "ADC", self.adc, self.indirectX)
        self.addInstruction(0x71, "ADC", self.adc, self.indirectY)
        
        self.addInstruction(0x29, "AND", self.and1, self.immediate)
        self.addInstruction(0x25, "AND", self.and1, self.zeroPage)
        self.addInstruction(0x35, "AND", self.and1, self.zeroPageX),
        self.addInstruction(0x2d, "AND", self.and1, self.absolute)
        self.addInstruction(0x3d, "AND", self.and1, self.absoluteX)
        self.addInstruction(0x39, "AND", self.and1, self.absoluteY)
        self.addInstruction(0x21, "AND", self.and1, self.indirectX)
        self.addInstruction(0x31, "AND", self.and1, self.indirectY)
        
        self.addInstruction(0x0a, "ASL", self.asl, self.accumulator)
        self.addInstruction(0x06, "ASL", self.asl, self.zeroPage)
        self.addInstruction(0x16, "ASL", self.asl, self.zeroPageX)
        self.addInstruction(0x0e, "ASL", self.asl, self.absolute)
        self.addInstruction(0x1e, "ASL", self.asl, self.absoluteX)
        
        self.addInstruction(0x24, "BIT", self.bit, self.zeroPage)
        self.addInstruction(0x2c, "BIT", self.bit, self.absolute),
        
        # True indicated that value must be interpreted as a relative branch instead of an address
        self.addInstruction(0x10, "BPL", self.bpl, self.zeroPage, True)
        self.addInstruction(0x30, "BMI", self.bmi, self.zeroPage, True)
        self.addInstruction(0x50, "BVC", self.bvc, self.zeroPage, True)
        self.addInstruction(0x70, "BVS", self.bvs, self.zeroPage, True)
        self.addInstruction(0x90, "BCC", self.bcc, self.zeroPage, True)
        self.addInstruction(0xB0, "BCS", self.bcs, self.zeroPage, True)
        self.addInstruction(0xD0, "BNE", self.bne, self.zeroPage, True)
        self.addInstruction(0xF0, "BEQ", self.beq, self.zeroPage, True)
       
        self.addInstruction(0x00, "BRK", self.brk, None)

        self.addInstruction(0xc9, "CMP", self.cmp, self.immediate)
        self.addInstruction(0xc5, "CMP", self.cmp, self.zeroPage)
        self.addInstruction(0xd5, "CMP", self.cmp, self.zeroPageX)
        self.addInstruction(0xcd, "CMP", self.cmp, self.absolute)
        self.addInstruction(0xdd, "CMP", self.cmp, self.absoluteX)
        self.addInstruction(0xd9, "CMP", self.cmp, self.absoluteY)
        self.addInstruction(0xc1, "CMP", self.cmp, self.indirectX)
        self.addInstruction(0xd1, "CMP", self.cmp, self.indirectY)
        
        self.addInstruction(0xe0, "CPX", self.cpx, self.immediate)
        self.addInstruction(0xe4, "CPX", self.cpx, self.zeroPage)
        self.addInstruction(0xec, "CPX", self.cpx, self.absolute)
        
        self.addInstruction(0xc0, "CPY", self.cpy, self.immediate)
        self.addInstruction(0xc4, "CPY", self.cpy, self.zeroPage)
        self.addInstruction(0xcc, "CPY", self.cpy, self.absolute)
        
        self.addInstruction(0xc6, "DEC", self.dec, self.zeroPage)
        self.addInstruction(0xd6, "DEC", self.dec, self.zeroPageX)
        self.addInstruction(0xce, "DEC", self.dec, self.absolute)
        self.addInstruction(0xde, "DEC", self.dec, self.absoluteX)

        self.addInstruction(0x49, "EOR", self.eor, self.immediate)
        self.addInstruction(0x45, "EOR", self.eor, self.zeroPage)
        self.addInstruction(0x55, "EOR", self.eor, self.zeroPageX)
        self.addInstruction(0x4d, "EOR", self.eor, self.absolute)
        self.addInstruction(0x5d, "EOR", self.eor, self.absoluteX)
        self.addInstruction(0x59, "EOR", self.eor, self.absoluteY)
        self.addInstruction(0x41, "EOR", self.eor, self.indirectX)
        self.addInstruction(0x51, "EOR", self.eor, self.indirectY)
        
        self.addInstruction(0x18, "CLC", self.clc, None)
        self.addInstruction(0x38, "SEC", self.sec, None)
        self.addInstruction(0x58, "CLI", self.cli, None)
        self.addInstruction(0x78, "SEI", self.sei, None)
        self.addInstruction(0xb8, "CLV", self.clv, None)
        self.addInstruction(0xd8, "CLD", self.cld, None)
        self.addInstruction(0xf8, "SED", self.sed, None)
        
        self.addInstruction(0xe6, "INC", self.inc, self.zeroPage)
        self.addInstruction(0xf6, "INC", self.inc, self.zeroPageX)
        self.addInstruction(0xee, "INC", self.inc, self.absolute)
        self.addInstruction(0xfe, "INC", self.inc, self.absoluteX)
       
        self.addInstruction(0x4c, "JMP", self.jmp, self.absolute)
        self.addInstruction(0x6c, "JMP", self.jmp, self.indirect)
 
        self.addInstruction(0x20, "JSR", self.jsr, self.absolute)

        self.addInstruction(0xa9, "LDA", self.lda, self.immediate)
        self.addInstruction(0xa5, "LDA", self.lda, self.zeroPage)
        self.addInstruction(0xb5, "LDA", self.lda, self.zeroPageX)
        self.addInstruction(0xad, "LDA", self.lda, self.absolute)
        self.addInstruction(0xbd, "LDA", self.lda, self.absoluteX)
        self.addInstruction(0xb9, "LDA", self.lda, self.absoluteY)
        self.addInstruction(0xa1, "LDA", self.lda, self.indirectX)
        self.addInstruction(0xb1, "LDA", self.lda, self.indirectY)
        
        self.addInstruction(0xa2, "LDX", self.ldx, self.immediate)
        self.addInstruction(0xa6, "LDX", self.ldx, self.zeroPage)
        self.addInstruction(0xb6, "LDX", self.ldx, self.zeroPageY)
        self.addInstruction(0xae, "LDX", self.ldx, self.absolute)
        self.addInstruction(0xbe, "LDX", self.ldx, self.absoluteY)
        
        self.addInstruction(0xa0, "LDY", self.ldy, self.immediate)
        self.addInstruction(0xa4, "LDY", self.ldy, self.zeroPage)
        self.addInstruction(0xb4, "LDY", self.ldy, self.zeroPageX)
        self.addInstruction(0xac, "LDY", self.ldy, self.absolute)
        self.addInstruction(0xbc, "LDY", self.ldy, self.absoluteX)

        self.addInstruction(0x4a, "LSR", self.lsr, self.accumulator)
        self.addInstruction(0x46, "LSR", self.lsr, self.zeroPage)
        self.addInstruction(0x56, "LSR", self.lsr, self.zeroPageX)
        self.addInstruction(0x4e, "LSR", self.lsr, self.absolute)
        self.addInstruction(0x5e, "LSR", self.lsr, self.absoluteX)

        self.addInstruction(0xea, "NOP", self.nop, None)
        
        self.addInstruction(0x09, "ORA", self.ora, self.immediate)
        self.addInstruction(0x05, "ORA", self.ora, self.zeroPage)
        self.addInstruction(0x15, "ORA", self.ora, self.zeroPageX)
        self.addInstruction(0x0d, "ORA", self.ora, self.absolute)
        self.addInstruction(0x1d, "ORA", self.ora, self.absoluteX)
        self.addInstruction(0x19, "ORA", self.ora, self.absoluteY)
        self.addInstruction(0x01, "ORA", self.ora, self.indirectX)
        self.addInstruction(0x11, "ORA", self.ora, self.indirectY)
        
        self.addInstruction(0xaa, "TAX", self.tax, None)
        self.addInstruction(0x8a, "TXA", self.txa, None)
        self.addInstruction(0xca, "DEX", self.dex, None)
        self.addInstruction(0xe8, "INX", self.inx, None)
        self.addInstruction(0xa8, "TAY", self.tay, None)
        self.addInstruction(0x98, "TYA", self.tya, None)
        self.addInstruction(0x98, "DEY", self.dex, None)
        self.addInstruction(0xc8, "INY", self.iny, None)
        
        self.addInstruction(0x2a, "ROL", self.rol, self.accumulator)
        self.addInstruction(0x26, "ROL", self.rol, self.zeroPage)
        self.addInstruction(0x36, "ROL", self.rol, self.zeroPageX)
        self.addInstruction(0x2e, "ROL", self.rol, self.absolute)
        self.addInstruction(0x3e, "ROL", self.rol, self.absoluteX)
        
        self.addInstruction(0x6a, "ROR", self.ror, self.accumulator)
        self.addInstruction(0x66, "ROR", self.ror, self.zeroPage)
        self.addInstruction(0x76, "ROR", self.ror, self.zeroPageX)
        self.addInstruction(0x6e, "ROR", self.ror, self.absolute)
        self.addInstruction(0x7e, "ROR", self.ror, self.absoluteX)
        
        self.addInstruction(0x40, "RTI", self.rti, None)
        
        self.addInstruction(0x60, "RTS", self.rts, None)

        self.addInstruction(0xe9, "SBC", self.sbc, self.immediate)
        self.addInstruction(0xe5, "SBC", self.sbc, self.zeroPage)
        self.addInstruction(0xf5, "SBC", self.sbc, self.zeroPageX)
        self.addInstruction(0xed, "SBC", self.sbc, self.absolute)
        self.addInstruction(0xfd, "SBC", self.sbc, self.absoluteX)
        self.addInstruction(0xf9, "SBC", self.sbc, self.absoluteY)
        self.addInstruction(0xe1, "SBC", self.sbc, self.indirectX)
        self.addInstruction(0xf1, "SBC", self.sbc, self.indirectY)

        self.addInstruction(0x85, "STA", self.sta, self.zeroPage)
        self.addInstruction(0x95, "STA", self.sta, self.zeroPageX)
        self.addInstruction(0x8d, "STA", self.sta, self.absolute)
        self.addInstruction(0x9d, "STA", self.sta, self.absoluteX)
        self.addInstruction(0x99, "STA", self.sta, self.absoluteY)
        self.addInstruction(0x81, "STA", self.sta, self.indirectX)
        self.addInstruction(0x91, "STA", self.sta, self.indirectY)

        self.addInstruction(0x9a, "TXS", self.txs, None)
        self.addInstruction(0xba, "TSX", self.tsx, None)
        self.addInstruction(0x48, "PHA", self.pha, None)
        self.addInstruction(0x68, "PLA", self.pla, None)
        self.addInstruction(0x08, "PHP", self.php, None)
        self.addInstruction(0x28, "PLP", self.plp, None)
        
        self.addInstruction(0x86, "STX", self.stx, self.zeroPage)
        self.addInstruction(0x96, "STX", self.stx, self.zeroPageY),
        self.addInstruction(0x8e, "STX", self.stx, self.absolute)
 
        self.addInstruction(0x84, "STY", self.sty, self.zeroPage)
        self.addInstruction(0x94, "STY", self.sty, self.zeroPageX)
        self.addInstruction(0x8c, "STY", self.sty, self.absolute)

        self.addInstruction(0xFF, "END", self.end, None)
        
        self.addData('BYTE', 1, self.decodeInt)
        self.addData('WORD', 2, self.decodeInt)
        
        self.defineLabelPattern(patternLabel)
        
        self.addSection("ORG", False, self.decodeAddr)
        
        self.setDataWithAddress(False)
        self.setComment(';')
        self.setWordSize(wordSize)
        self.setInstructionSize(instructionSize)
        self.setAddressSize(addressSize)
        
    def translateIntoOffset(self, addressing):
        return self.zeroPage
        
    def clear(self):
        super(Chip, self).clear()
        # reset the Stack Pointer to its starting value
        self.SP.set(0x1ff)
    
    #
    # implementation of methods used to decode data    
    #
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
        
    def decodeReg(self, string):
        return 0
    
    def decodeAddr(self, string):
        return self.decodeInt(string)
    
    #
    # implementation of callback used when executing code
    #
        
    def getAddress(self, board, parameter):
        ptype = parameter.getAddressing()
        pvalue = parameter.getValue()
        psize = parameter.getSize()
        if ptype == self.zeroPage or ptype == self.absolute:
            address = libproc.ltoui(pvalue, psize)
        elif ptype == self.zeroPageX or ptype == self.absoluteX:
            address = libproc.ltoui(pvalue, psize)
            address += self.regX.get()
        elif ptype == self.zeroPageY or ptype == self.absoluteY:
            address = libproc.ltoui(pvalue, psize)
            address += self.regY.get()
        elif ptype == self.indirect:
            address = libproc.ltoui(pvalue, psize)
            address = board.memory.get(address, self.getAddressSize())
        elif ptype == self.indirectX:
            address = libproc.ltoui(pvalue, psize) + self.regX.get()
            address = board.memory.get(address, self.getAddressSize())
        elif ptype == self.indirectY:
            address = libproc.ltoui(pvalue, psize)
            address = board.memory.get(address, self.getAddressSize())
            address = address + self.regY.get()
        else:
            print "NOT YET IMPLEMENTED"
        return libproc.ltoui(address, self.getAddressSize())
    
    def getData(self, board, parameter, datasize):
        ptype = parameter.getAddressing()
        pvalue = parameter.getValue()
        psize = parameter.getSize()
        if ptype == self.accumulator:
            return self.regA.get()
        if ptype == self.immediate:
            return libproc.ltoi(pvalue, psize)
        else:
            address = self.getAddress(board, parameter)
            return board.memory.get(address, datasize)
        
    def setData(self, board, parameter, data):
        ptype = parameter.getAddressing()
        pvalue = parameter.getValue()
        psize = parameter.getSize()
        if ptype == self.accumulator:
            self.regA.set(data)
            return
        address = self.getAddress(board, parameter)
        board.memory.set(address, self.getWordSize(), data)    
        
    def getHigh(self, value):
        res = value >> (self.getWordSize() * 8)
        res = res & 0xff
        return res 
    
    def getLow(self, value):
        res = value & 0xff
        return res         

    def adc(self, board, parameterList):
        value = self.getData(board, parameterList[0], self.regA.getSize())
        value = libproc.ltoui(value, self.getWordSize())
        #self.regA.add(value + self.carry.get())
        carry = self.carry.get()
        a = libproc.ltoui(self.regA.get(), self.regA.getSize())                
        res = a + value + carry
        if (res > 255):
            self.carry.set(1)
        else:
            self.carry.set(0)
            
        # check overflow: if bit 8 of each value is equal, overflow if bit 8 of result is different
        mask = 1 << (self.regA.getSize() * 8 - 1)
        b1 = a & mask
        b2 = value & mask
        br = res & mask
        if (b1 == b2) and (b1 != br): 
            self.overflow.set(1)
        else:
            self.overflow.set(0)    

        self.regA.set(res)        
        
    def sbc(self, board, parameterList):
        # operation are done with unsigned integer to detect carry and overflow
        # res = A + ~ M + C  
        value = self.getData(board, parameterList[0], self.regA.getSize())
        carry = self.carry.get()
        cvalue = libproc.complement1(value, self.getWordSize())
        cvalue = libproc.ltoui(cvalue, self.getWordSize())
        a = libproc.ltoui(self.regA.get(), self.regA.getSize())
        res = a + cvalue + carry
        if res > 255:
            self.carry.set(1)
        else:
            self.carry.set(0)
        if res > 127 or res < -128:
            self.overflow.set(1)
        else:
            self.overflow.set(0)
        self.regA.set(res)

    def and1(self, board, parameterList):
        value = self.getData(board, parameterList[0], self.regA.getSize())
        self.regA.set(value & self.regA.get())
 
    def asl(self, board, parameterList):
        value = self.getData(board, parameterList[0], self.regA.getSize())
        if (value < 0):
            self.carry.set(1)
        else:
            self.carry.set(0)
        # shift on left and set bit 0 to 0: mask with -2/xxxxFE
        value = (value << 1) & -2
        self.setData(board, parameterList[0], value)
        if value < 0:
            self.negative.set(1)
        else:
            self.negative.set(0)
        if value == 0:
            self.zero.set(1)
        else:
            self.zero.set(0)
        
        
    def bit(self, board, parameterList):
        value = self.getData(board, parameterList[0], self.regA.getSize())
        value = value & self.regA.get()
        if (value == 0):
            self.zero.set(1)
        else:
            self.zero.set(0)
        # negative is eet if bit 7 is set then negative
        if (value < 0):
            self.negative.set(1)
        else:
            self.negative.set(0)
        # overflow is set if bit 6 is set: nothing related to overflow
        # must be coded explicitely (bit 6: 5 shift)
        if value & (1 << 5):
            self.overflow.set(1)
        else:
            self.overflow.set(0)
    
    def dec(self, board, parameterList):
        value = self.getData(board, parameterList[0], self.getWordSize())
        value = libproc.ltoi(value - 1, self.getWordSize()) 
        self.setData(board, parameterList[0], value)
        if (value == 0):
            self.zero.set(1)
        else:
            self.zero.set(0)
        if (value < 0):
            self.negative.set(1)
        else:
            self.negative.set(0)

    def eor(self, board, parameterList):
        value = self.getData(board, parameterList[0], self.regA.getSize())
        self.regA.set(value ^ self.regA.get())
        
    def inc(self, board, parameterList):
        value = self.getData(board, parameterList[0], self.getWordSize())
        value = libproc.ltoi(value + 1, self.getWordSize())
        self.setData(board, parameterList[0], value)
        if (value == 0):
            self.zero.set(1)
        else:
            self.zero.set(0)
        if (value < 0):
            self.negative.set(1)
        else:
            self.negative.set(0)

    def jsr(self, board, parameterList):
        address = self.getAddress(board, parameterList[0])
        pc = self.PC.get() - 1
        val = self.getHigh(pc)
        board.memory.set(self.SP.get(), self.getWordSize(), val)
        self.SP.set(self.SP.get() - 1)
        val = self.getLow(pc)
        board.memory.set(self.SP.get(), self.getWordSize(), val)
        self.SP.set(self.SP.get() - 1)
        self.PC.set(address)


    def lsr(self, board, parameterList):
        value = self.getData(board, parameterList[0], self.regA.getSize())
        b0 = 0
        if (value & 1) > 0:
            b0 = 1
        # shift on right and set bit 7 to 0
        value = (value >> 1)
        mask = ~(1 << (self.getWordSize() * 8 - 1))
        value = value & mask
        self.setData(board, parameterList[0], value)
        self.carry.set(b0)
        # cannot be negative: sign bit set to 0
        self.negative.set(0)
        if value == 0:
            self.zero.set(1)
        else:
            self.zero.set(0)

    def ora(self, board, parameterList):
        value = self.getData(board, parameterList[0], self.regA.getSize())
        self.regA.set(value | self.regA.get())

    def rol(self, board, parameterList):
        value = self.getData(board, parameterList[0], self.regA.getSize())
        b7 = 0
        if (value < 0):
            b7 = 1
        # shift on left and set bit 0 to 0: mask with -2/xxxxFE
        value = (value << 1) & -2
        # set bit 0 with carry
        value = value | self.carry.get()
        self.setData(board, parameterList[0], value)
        self.carry.set(b7)
        if value < 0:
            self.negative.set(1)
        else:
            self.negative.set(0)
        if value == 0:
            self.zero.set(1)
        else:
            self.zero.set(0)
 
    def ror(self, board, parameterList):
        value = self.getData(board, parameterList[0], self.regA.getSize())
        b0 = 0
        if (value & 1) > 0:
            b0 = 1
        # shift on right and set bit 7 to zero
        value = (value >> 1)
        mask = ~(1 << (self.getWordSize() * 8 - 1))
        value = value & mask
        # set bit 7 with carry: use mask 8000...
        mask = self.carry.get() << (self.getWordSize() * 8 - 1)
        value = value | mask
        self.setData(board, parameterList[0], value)
        self.carry.set(b0)
        if value < 0:
            self.negative.set(1)
        else:
            self.negative.set(0)
        if value == 0:
            self.zero.set(1)
        else:
            self.zero.set(0)
 
    def rti(self, board, parameterList):
        self.SP.set(self.SP.get() - 1)
        self.PSR.set(board.memory.get(self.SP.get(), self.PSR.getSize()))
        self.SP.set(self.SP.get() - 1)
        low = board.memory.get(self.SP.get(), self.getWordSize())
        self.SP.set(self.SP.get() - 1)
        high = board.memory.get(self.SP.get(), self.getWordSize())
        value = (high << 4) + low
        self.PC.set(value)


    def rts(self, board, parameterList):
        self.SP.set(self.SP.get() + 1)
        low = board.memory.get(self.SP.get(), self.getWordSize())
        self.SP.set(self.SP.get() + 1)
        high = board.memory.get(self.SP.get(), self.getWordSize())
        value = (high << 4) + low
        self.PC.set(value + 1)

    def txs(self, board, parameterList):
        self.SP.set(self.regX.get())

    def tsx(self, board, parameterList):
        self.regX.set(self.SP.get())

    def pha(self, board, parameterList):
        board.memory.set(self.SP.get(), self.regA.getSize(), self.regA.get())
        self.SP.set(self.SP.get() - 1)

    def pla(self, board, parameterList):
        self.SP.set(self.SP.get() + 1)
        self.regA.set(board.memory.get(self.SP.get(), self.regA.getSize()))

    def php(self, board, parameterList):
        board.memory.set(self.SP.get(), self.PSR.getSize(), self.PSR.get())
        self.SP.set(self.SP.get() - 1)

    def forceIndic(self, indic):
        mask = 1 << indic.getRank()
        if (self.PSR.get() & mask) != 0:
            indic.set(1)
        else:
            indic.set(0)
            
    def plp(self, board, parameterList):
        self.SP.set(self.SP.get() + 1)
        self.PSR.set(board.memory.get(self.SP.get(), self.PSR.getSize()))
        # set all indicator based on new SP value
        self.forceIndic(self.carry)
        self.forceIndic(self.zero)
        self.forceIndic(self.interrupt)
        self.forceIndic(self.decimal)
        self.forceIndic(self.brkInd)
        self.forceIndic(self.overflow)
        self.forceIndic(self.negative)
    
    def ldreg(self, board, reg, parameterList):
        value = self.getData(board, parameterList[0], reg.getSize())
        reg.set(value)
        
    def lda(self, board, parameterList):
        self.ldreg(board, self.regA, parameterList)
        
    def ldx(self, board, parameterList):
        self.ldreg(board, self.regX, parameterList)
        
    def ldy(self, board, parameterList):
        self.ldreg(board, self.regY, parameterList)
    
    def streg(self, board, reg, parameterList):
        self.setData(board, parameterList[0], reg.get())
        
    def sta(self, board, parameterList):
        self.streg(board, self.regA, parameterList)
        
    def stx(self,board, parameterList):
        self.streg(board, self.regX, parameterList)
        
    def sty(self,board, parameterList):
        self.streg(board, self.regY, parameterList)
 
    def tax(self, board, parameterList):
        self.regX.set(self.regA.get())
    
    def txa(self, board, parameterList):
        self.regA.set(self.regX.get())
    
    def tay(self, board, parameterList):
        self.regY.set(self.regA.get())
    
    def tya(self, board, parameterList):
        self.regA.set(self.regY.get())

    def dex(self, board, parameterList):
        self.regX.set(self.regX.get() - 1)
    
    def inx(self, board, parameterList):
        self.regX.set(self.regX.get() + 1)

    def dey(self, board, parameterList):
        self.regY.set(self.regY.get() - 1)
    
    def iny(self, board, parameterList):
        self.regY.set(self.regY.get() + 1)
        
    def bRelatif(self, board, parameterList):
        value = libproc.ltoi(parameterList[0].getValue(), parameterList[0].getSize())
        self.PC.set(self.PC.get() + value)
           
    def bpl(self, board, parameterList):
        if (self.negative.get() == 0):
            self.bRelatif(board, parameterList)
        
    def bmi(self, board, parameterList):
        if (self.negative.get() == 1):
            self.bRelatif(board, parameterList)
    
    def bvc(self, board, parameterList):
        if (self.overflow.get() == 0):
            self.bRelatif(board, parameterList)
    
    def bvs(self, board, parameterList):
        if (self.overflow.get() != 0):
            self.bRelatif(board, parameterList)
    
    def bcc(self, board, parameterList):
        if (self.carry.get() == 0):
            self.bRelatif(board, parameterList)
    
    def bcs(self, board, parameterList):
        if (self.carry.get() != 0):
            self.bRelatif(board, parameterList)
    
    def bne(self, board, parameterList):
        if (self.zero.get() == 0):
            self.bRelatif(board, parameterList)
    
    def beq(self, board, parameterList):
        if (self.zero.get() != 0):
            self.bRelatif(board, parameterList)
        
    def clc(self, board, parameterList):
        self.carry.set(0)
        
    def sec(self, board, parameterList):
        self.carry.set(1)
 
    def cli(self, board, parameterList):
        self.interrupt.set(0)
        
    def sei(self, board, parameterList):
        self.interrupt.set(1)
        
    def clv(self, board, parameterList):
        self.overflow.set(0)
        
    def cld(self, board, parameterList):
        self.decimal.set(0)
 
    def sed(self, board, parameterList):
        self.decimal.set(1)
        raise ExecError(Error.error, "Decimal mode not implemented")
   
    def cmpr(self, board, reg, parameterList):
        value = self.getData(board, parameterList[0], reg.getSize())
        regvalue = libproc.ltoi(reg.get(), reg.getSize())
        if (regvalue == value):
            self.zero.set(1)
        else:
            self.zero.set(0)
        if regvalue >= value:
            self.carry.set(1)
        else:
            self.carry.set(0)
        if (regvalue - value < 0):
            self.negative.set(1)
        else:
            self.negative.set(0)
    
    def jmp(self, board, parameterList):
        address = self.getAddress(board, parameterList[0])
        self.PC.set(address)
    
    def cmp(self, board, parameterList):
        self.cmpr(board, self.regA, parameterList)
        
    def cpx(self, board, parameterList):
        self.cmpr(board, self.regX, parameterList)
        
    def cpy(self, board, parameterList):
        self.cmpr(board, self.regY, parameterList)
        
    def nop(self, board, parameterList):
        # do nothing: reserve space to patch code
        # when coding on real machine
        return

    def brk(self, board, parameterList):
        raise ExecError(Error.error, "BRK called" )
 
    def end(self, board, parameterList):
        self.setEndProgram(True)
    