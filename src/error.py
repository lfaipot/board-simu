# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#

class Error(Exception):
    "Base class for exception"
    
    warning  = 0
    error    = 1
    critical = 2
    end      = 3 
    
    def __init__(self, severity, msg = ""):
        self.severity = severity
        self.msg = msg
        
    def __str__(self):
        return "EXCEPTION: " + self.msg
    
    @classmethod
    def whenHappen(cls, fct):
        cls.fct = fct
        
    def display(self):
        Error.fct(self)
