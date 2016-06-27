# -*- coding:utf-8 -*- 
#
# Copyright(C) 2014 Laurent Faipot (laurent.faipot@free.fr). All rights reserved.
#

import webbrowser
        
def display(fileName):
    url = fileName
    
    # On Mac OS X, open doesn't work if URL doesn't contain protocol
    # do not add extra "/"
    if url[0:5] != "http:" and url[0:5] != "file:":
        url = "file:" + url
    
    # new=2: new browser tab if possible
    # autoraise: windows is raised if possible
    webbrowser.open(url, new=2, autoraise=True)