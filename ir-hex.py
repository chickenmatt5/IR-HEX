#!/usr/bin/python

"""
Infinite Recursion returns! Back and ready for Generation 6,
IR-HEX has a purpose distinctly different from the IR-GTS of
old. Gone are the easy-to-spoof Global Trade Station servers,
but there's still binary Pokemon files to analyze, and
infinity won't recurse itself! This project now focuses on
analysis and rudimentary math-based legit checks. All wrapped
up in more infinite recursion than ever before!

- chickenmatt5
"""

import os
from platform import system
from array import array

from src.stats import statSetup, statAnalyze, statLog


verVar = "0.1"

introString = """ ___________       _   _  _______   __
|_   _| ___ \     | | | ||  ___\ \ / /
  | | | |_/ /_____| |_| || |__  \ V / 
  | | |    /______|  _  ||  __| /   \ 
 _| |_| |\ \      | | | || |___/ /^\ \ 
 \___/\_| \_|     \_| |_/\____/\/   \/                                                                                                              
"""

print "Welcome to\n" + introString + "version " + verVar


while True:
    while True:
        while True:
            print '\nPlease enter the .pk6 file path'
            print '(To exit, type "exit" and hit enter)'
            filePath = raw_input().strip()
            if filePath == 'exit': exit()
            filePath = os.path.normpath(filePath)
            if system() != 'Windows':
                filePath = filePath.replace('\\', '')
        
            if filePath.startswith('"') or filePath.startswith("'"):
                filePath = filePath[1:]
            if filePath.endswith('"') or filePath.endswith("'"):
                filePath = filePath[:-1]
            elif not os.path.exists(filePath): print '\nThat file does not appear to exist, try again.'
            elif not filePath.lower().endswith('.pk6'): print '\nThat does not appear to be a .pk6 file, try again.'
            if os.path.exists(filePath) and filePath.lower().endswith('.pk6'): break
            
        with open(filePath, 'rb') as holder:
            pk6 = holder.read()

        if len(pk6) == 232:
            print '\nThis Pokemon does not have any battle stats.\nAdding battle stats will come in a future update.'
        if len(pk6) != 260:
            print '\nInvalid filesize: %d bytes. Needs to be either 232 or 260 bytes.' % len(pk6)
        
        if len(pk6) == 260: break
        
    p = array('B')
    p.fromstring(pk6)
    
    s = statSetup(p, pk6, filePath)
    
    print '\nBeginning data readout:\n'
    print s
    print '\nBeginning analysis:'
    a = statAnalyze(p, filePath)
    print a + '\n'
    if a == '':
        print 'No problems detected.'
    statLog(s)
    print '\nEnd of readout.'