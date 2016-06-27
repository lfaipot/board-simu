# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#

debugEnabled = False
#debugEnabled = True

def log(string):
    print string
    
def debug(level, string):
    if (not debugEnabled):
        return
    
    indent = ""
    for _ in range(level):
        indent += " "
    print indent + string
