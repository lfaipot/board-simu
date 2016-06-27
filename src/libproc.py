# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#

def ltoi(value, size):
    "convert long integer into sized integer"
    # value is extracted from memory without taking care of sign
    # determine sign of integer
    if (size <= 0):
        return 0
    mask = 1 << (size * 8 - 1)
    if (value & mask):
        # propagate sign bit
        mask = -1 << (size * 8)
        value = value | mask
    else:
        mask = -1 << (size * 8)
        mask = ~mask
        value = value & mask
    return (value)

def ltoui(value, size):
    "convert long integer into sized unsigned integer"
    # mask: fulfill with 1 (setting to -1)
    # just keep 1s on part to keep
    mask = -1
    mask = mask << (size * 8)
    mask = ~mask
    value = value & mask
    #print "value: " + str(value) + " hex: " + str(ltoh(value, 4))
    return value

def ltoa(value, size):
    "convert long integer into ASCII of sized integer"
    return str(ltoi(value, size))

def ltoh(value, size):
    "convert long integer into HEX ASCII of sized integer"
    value = ltoi(value, size)
    nbits = size * 8
    s = hex((value + (1 << nbits)) % (1 << nbits))
    s = s[2:]
    return s.rjust(size * 2, '0').upper()

def complement1(value, size):
    #mask: must be 000..FF on part to keep
    mask = -1
    mask = mask << (size * 8)
    mask = ~mask
    res = ~value & mask
    #print "COMPLEMENT1: size: " + str(size) + " mask: " + str(hex(mask)) + " value: " + str(hex(value)) + " res: " + str(hex(res))
    return res

def complement2(value, size):
    res = -value + 1
    #print "COMPLEMENT2: value: " + str(hex(value)) + " res: " + str(hex(res))
    return res