# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#
#class Program(Assembly):
import re
import trace
from error import *

class ProgramError(Error):
    def __init__(self, severity, msgList):
        Error.__init__(self, severity)
        self.msgList = msgList
        
    def __str__(self):
        msg = ""
        for l in self.msgList:
            if (len(msg) > 0):
                msg += "\n"
            msg += l
        return msg
    
class Operand:
    
    def __init__(self):
        self.text        = ""
        self.addressing  = None
        self.isLabel     = False
        self.label       = ""
        self.value       = 0
        self.size        = -1
    
    def debug(self, comment):
        print comment
        print "    text:       " + self.text
        print "    addressing: " + str(self.addressing)
        print "    isLabel:    " + str(self.isLabel)
        if self.isLabel:
            print "    label:      " + self.label
        print "    value:      " + str(self.value) + " " + str(hex(self.value))
        print "    size:       " + str(self.size)
        
class InstructionLine:
 
    Unknown     = 0   
    Directive   = 1
    Data        = 2
    Code        = 3
    Label       = 4
    
    def __init__(self):
        self.type       = self.Unknown
        self.line       = ""
        self.lineNb     = -1
        self.mnemonic   = ""
        self.opcode     = -1
        self.size       = -1
        self.value      = -1
        self.address    = -1
        self.operand    = ""
        self.withLabel  = False
        self.isOffset   = False
        self.label      = ""
        self.operandList= []
        self.errorList  = []
        
    def debug(self, comment = ""):
        print comment
        print str(self.lineNb) + ": " + self.line
        if self.type == self.Unknown:
            print "UNKNOWN"
        if self.type == self.Directive:
            print "DIRECTIVE"
        if self.type == self.Data:
            print "DATA"
        if self.type == self.Code:
            print "CODE"
        if self.type == self.Label:
            print "LABEL"

        print "    lineNb:   " +str(self.lineNb)
        print "    mnemonic: " + self.mnemonic
        print "    opcode:   " + str(hex(self.opcode))
        print "    address:  " + str(self.address)
        print "    size:     " + str(self.size)
        print "    value:    " + str(self.value)
        print "    isOffset: " + str(self.isOffset)
        if self.withLabel:
            print "    label:     " + self.label
        for op in self.operandList:
            op.debug("")
        for error in self.errorList:
            print error
            
    def getErrorList(self):
        return self.errorList
    
    def getLineNb(self):
        return self.lineNb
    
    def getLabel(self):
        if self.type == self.Label:
            # add ":" at the end as it is an isolated label
            return self.label + ":"
        else:
            return self.label
    
    def getMnemonic(self):
        return self.mnemonic
    
    def getAddress(self):
        return self.address
    
    def getOperand(self):
        return self.operand
            
class Program:

#   def __init__(self):
#       Assembly.__init__(self)

    def __init__(self):
        self.code = 0;
        self.loadAddress = 0
        self.instructionList = []
        self.readingData = True

    def setReadingData(self, readingData):
        self.readingData = readingData
        
    def isReadingData(self):
        print "isReadingData: "
        print str(self.readingData)
        return self.readingData
    
    def setCodeBase(self, value):
        self.code = value
        self.loadAddress = value
        
    def getCodeBase(self):
        return self.code
    
    def getLoadAddress(self):
        return self.loadAddress
            
    def isDirective(self, chip, itemList):
        trace.debug(1, "PROGRAM isDirective")
        trace.debug(2, "mnemonic: " + str(itemList[0].upper())) 
        found = False
        for section in chip.getSectionSet():
            mnemonic = section.getName()
            if itemList[0].upper() == section.getName():
                self.setReadingData(section.isData())
                found= True
                break
            
        if not found:
            return None
                
        instLine = InstructionLine()
        instLine.type = instLine.Directive;
        instLine.mnemonic = mnemonic
                
        fct = section.getFct()
        if fct:
            # it means that an operand is expected
            if len(itemList) <= 1:
                instLine.errorList.append(mnemonic + ": operand missing")
            else:
                addressStr = itemList[1]
                instLine.operand = addressStr
                instLine.address = fct(addressStr)
        else:
            if len(itemList) > 1:
                instLine.errorList.append(mnemonic + ": no operand expected")

        return instLine
            
    def isData(self, chip, itemList):
        trace.debug(1, "PROGRAM isData")
        #
        # look for at least one keyword
        # line can be
        #   <LABEL>   keyword  value
        # or
        #   <LABEL>    address  value
        # if dataWithAddress is True
        #
        found = False
        maxi = len(itemList)
        if maxi > 2:
            maxi = 2 
            
        for i in range(maxi):
            for data in chip.getDataSet():
                string = itemList[i].upper()
                mnemonic = data.getMnemonic()
                if re.match("^" + mnemonic + "$", string):
                #if itemList[i].upper() == mnemonic.upper():
                    found = True
                    index = i
                    break
            if found:
                break
            
        if not found:
            return None
        
        instLine = InstructionLine()
        instLine.type = instLine.Data
        if (chip.isDataWithAddress()):
            instLine.address = chip.decodeAddr(string)
            if index < (len(itemList) - 1):
                fct             = data.getFct()
                instLine.value  = fct(itemList[index + 1])
            else:
                instLine.value  = 0
            # no mnemonic to indicate data size: use default word size    
            instLine.size    = chip.getWordSize()
            if index == 1:
                # there is a label before
                instLine.withLabel = True
                instLine.label = itemList[0]
        else:
            instLine.mnemonic = string
            instLine.withLabel = False
            if index > 0:
                instLine.withLabel = True
                instLine.label     = itemList[0]
            instLine.operand = itemList[index + 1]
            fct            = data.getFct()
            instLine.value = fct(instLine.operand)
            instLine.size = data.getSize()
        return instLine
    
    def decodeOperand(self, chip, instLine, operandStr):
        trace.debug(1, "PROGRAM decodeOperand")
        for addressing in chip.getAddressingSet():
            trace.debug(4, "addressing " + str(addressing))
            trace.debug(4, "check against: " + addressing.getPattern())
            pattern = re.compile("^" + addressing.getPattern() + "$")
            match = pattern.match(operandStr)
            if (match):
                trace.debug(4, "--> matching: " + addressing.getPattern())
                # as pattern could contain several groups (to match label and real value)
                # we need to extract the one that matched
                string = None
                trace.debug(4, "Groups: " + str(match.groups()))
                for g in match.groups(): 
                    if (g):
                        string = g
                        break
                string = str(string)
                # if label, store it
                trace.debug(4, "Operand string: " + string)
                operand = Operand()
                operand.text = operandStr
                operand.addressing = addressing
 
                # if the operand can be either a value or a label (several group), check if it is a label
                # if there is one group, it can be a register name
                operand.isLabel = False
                if len(match.groups()) > 1:
                    trace.debug(4, "labelPattern: " + chip.getLabelPattern())
                    pattern = re.compile("^" + chip.getLabelPattern() + "$")
                    match = pattern.match(string)

                    if (match):
                        # special case for instruction performing relative branch
                        # LABEL, used to reference address, could need to be converted with an offset
                        # computed addressing mode could need to change accordingly 
                        trace.debug(4, "---> LABEL")
                        operand.isLabel = True
                        operand.size = chip.getAddressSize()
                        operand.label = string
                        if (instLine.isOffset):
                            operand.addressing = chip.translateIntoOffset(operand.addressing)
                            operand.size = operand.addressing.getSize()
                if not operand.isLabel:
                    trace.debug(4, "---> NOT A LABEL")
                    # decode value depending on operand type
                    fct = addressing.getProcessing()
                    operand.value = fct(string)
                    operand.size  = addressing.getSize()
                return operand
        
        error = operandStr + ": operand type not recognized"
        instLine.errorList.append(error)
        return None
    
    def findOpcode(self, chip, instLine):
        trace.debug(1, "PROGRAM findOpCode")
        trace.debug(2, "mnemonic: " + instLine.mnemonic)
        for chipInst in chip.getInstructionSet():
            trace.debug(3, "comparing with " + chipInst.getMnemonic())
            if instLine.mnemonic == chipInst.getMnemonic():
                found = True
                addressingList = chipInst.getAddressing()
                trace.debug(4, "nb of operands " + str(len(instLine.operandList)) + " compared with " + str(len(addressingList)))
                if len(instLine.operandList) == len(addressingList):
                    trace.debug(4, "--> compare operand")
                    for i in range(len(instLine.operandList)):
                        trace.debug(4, "  compare " + str(instLine.operandList[i].addressing) + " and " + str(addressingList[i]))
                        if instLine.operandList[i].addressing != addressingList[i]:
                            #trace.debug(4, "---> AT LEAST ONE DOESN'T MACH: NOT FOUND")
                            found = False
                            break
                    if found:
                        #print "---> FOUND"
                        instLine.opcode = chipInst.getOpcode()
                        return True
                else:
                    # number of operands doesn't match
                    found = False

        if not found:
            error =  instLine.mnemonic + ": operand type does not match"
            instLine.errorList.append(error)
            return False
                     
        return True
    
    def isCode(self, chip, itemList):
        trace.debug(1, "PROGRAM isCode")
        # look for at least an instruction with the same opcode
        # line can be
        # <LABEL> OPCODE <OPERAND>
        # so opcode can be in position 0 or 1
        maxi = len(itemList)
        if maxi > 2:
            maxi = 2 
        
        foundMnemonic = False
        for i in range(maxi):
            for chipInst in chip.getInstructionSet():
                mnemo = chipInst.getMnemonic()
                if itemList[i].upper() == mnemo.upper():
                    foundMnemonic = True
                    index = i
                    break
            if foundMnemonic:
                break
            
        if not foundMnemonic:
            return None
        
        instLine = InstructionLine()
        instLine.type = instLine.Code
        instLine.mnemonic = itemList[index].upper()
        instLine.size = chip.getInstructionSize()
        instLine.withLabel = False
        if index > 0:
            instLine.withLabel = True
            instLine.label     = itemList[0]
        
        # flag indicating if zero page is an address or a displacement is present
        # moreover, when looking for operand type, consider label as a zeroPage instead of absolute
        instLine.isOffset = chipInst.isOffset()

        instLine.operand = ""
        instLine.operandList = []
        
        if index < (len(itemList) - 1):
            if (chip.getOperandSeparator()):
                # multiple operands per instruction
                # TODO: split operand list and decode each operand
                instLine.errorList.append("Multiple operand not implemented: contact program author")
                return None
            else:
                instLine.operand = itemList[index + 1]
                operand = self.decodeOperand(chip, instLine, instLine.operand)
                if (not operand):
                    # inst contains error report
                    return instLine
                instLine.operandList.append(operand)
                
        #if not self.findOpcode(chip, inst):
        #    return None
        self.findOpcode(chip, instLine)
        return instLine
        
    def isLabel(self, chip, itemList):
        trace.debug(1, "PROGRAM isLabel")
        if len(itemList) == 1:
            p = re.match("^(" + chip.getLabelPattern() + ")\:$", itemList[0])
            if p:
                label = p.group(1)
                instLine = InstructionLine()
                instLine.type = instLine.Label
                instLine.label = label
                instLine.size = 0
                return instLine
        return None

    def analyzeFile(self, filename, chip):
        trace.debug(1, "PROGRAM analyzeFile")
        f = open(filename, "r")
        lineNb = 0
        
        for line in f:
            lineNb += 1
            
            # remove comments and ignore empty lines
            line = line.split(chip.getComment(), 1)[0]
            # split using spaces/tabs as separators
            itemList = line.split()
            if len(itemList) == 0:
                continue
            
            trace.debug(2, line)
            # 1st step: analyze line to determine its type
            # and store various item
            error = False
            msg = ""
            instLine = None
            try:
                instLine = self.isDirective(chip, itemList)
                if not instLine:
                    instLine = self.isCode(chip, itemList)
                if not instLine:
                    instLine = self.isData(chip, itemList)
                if not instLine:
                    instLine = self.isLabel(chip, itemList)
            except Error as e:
                error = True
                msg = str(e)
            if not instLine or error:
                instLine = InstructionLine()
                if error:
                    instLine.errorList.append(msg)
                else:
                    instLine.errorList.append("Invalid mnemonic " + itemList[0])
            
            instLine.line = line
            instLine.lineNb = lineNb
            self.instructionList.append(instLine)
                
    def setAddrDirective(self, chip, instLine):
        trace.debug(1, "PROGRAM setAddrDirective")
        self.loadAddress = instLine.address
        
    def setAddrData(self, chip, instLine):
        trace.debug(1, "PROGRAM setAddrData")
        if (instLine.address < 0):
            instLine.address = self.loadAddress
            self.loadAddress += instLine.size
        else:
            # address specified at data definition
            self.loadAddress = instLine.address + instLine.size
        if instLine.withLabel:
            self.labelDict[instLine.label] = instLine.address

    def setAddrCode(self, chip, instLine):
        trace.debug(1, "PROGRAM setAddrCode")
        instLine.address = self.loadAddress
        self.loadAddress += instLine.size
        if instLine.withLabel:
            self.labelDict[instLine.label] = instLine.address
        for operand in instLine.operandList:
            self.loadAddress += operand.size
            
    def setAddrLabel(self, chip, instLine):
        instLine.address = self.loadAddress
        self.labelDict[instLine.label] = instLine.address

    def setAddr(self, board):
        for instLine in self.instructionList:
            if instLine.type == instLine.Directive:
                self.setAddrDirective(board.chip, instLine)
            if instLine.type == instLine.Data:
                self.setAddrData(board.chip, instLine)
            elif instLine.type == instLine.Code:
                self.setAddrCode(board.chip, instLine)
            elif instLine.type == instLine.Label:
                self.setAddrLabel(board.chip, instLine)
            
    def resolveLabel(self, board):
        for instLine in self.instructionList:
            for operand in instLine.operandList:
                if operand.isLabel:
                    try:
                        value = self.labelDict[operand.label]
                        if instLine.isOffset:
                            operand.value = value - (instLine.address +  instLine.size + operand.size)
                            mini = - (2 ** (operand.size * 8 - 1))
                            maxi = 2 ** (operand.size * 8 - 1) - 1
                            if operand.value < mini or operand.value > maxi:
                                instLine.errorList.append(operand.label + ": branch out of range")
                        else:
                            operand.value = value
                    except:
                        instLine.errorList.append(operand.label + ": unknown label")

    def loadCode(self, board):
        trace.debug(1, "PROGRAM loadCode")
        memory = board.memory
        codeAddress = -1
        for instLine in self.instructionList:
            if instLine.type == instLine.Data:
                memory.set(instLine.address, instLine.size, instLine.value)
            elif instLine.type == instLine.Code:
                address = instLine.address
                if (codeAddress == -1):
                    codeAddress = address
                memory.set(address, instLine.size, instLine.opcode)
                address += instLine.size
                for operand in instLine.operandList:
                    memory.set(address, operand.size, operand.value)
                    address += operand.size
        
        if (codeAddress == -1):
            raise ProgramError(Error.error, ["No instruction"])
            return False
        self.setCodeBase(codeAddress)
        return True
        
    def load(self, fileName, board):
        trace.debug(1, "PROGRAM load")
        chip = board.chip
        
        self.instructionList = []
        self.errorList = []
        self.labelDict = {}
        
        self.analyzeFile(fileName, chip)
        self.setAddr(board)
        self.resolveLabel(board)
        # collect all error messages
        for instLine in self.instructionList:
            for error in instLine.errorList:
                msg = "Line " + str(instLine.lineNb) + ": "+ error 
                self.errorList.append(msg)

        if len(self.errorList) > 0:
            raise ProgramError(Error.error, self.errorList)
            return False
        return self.loadCode(board)
    
    def getProgram(self):
        return self.instructionList
    
    def getInstructionList(self):
        self.reducedInstructionList = []
        for instLine in self.instructionList:
            if (instLine.type == instLine.Code) or (instLine.type == instLine.Label):
                self.reducedInstructionList.append(instLine)
        return self.reducedInstructionList
    
    def getInstruction(self, index):
        return self.reducedInstructionList[index]