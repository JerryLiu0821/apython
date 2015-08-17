import os,re
import commands
import logging


def writeFile(strlist, filename):
    '''
    parm: list want to write, filename for list to write
    return: True if write successful otherwise False
    '''
    if strlist is None:
        return False
    fp = open(filename, 'w+')
    try:
        for line in strlist:
            fp.write(line + '\r\n')
        fp.close()
    except IOError:
        print IOError
        fp.close()
        return False
    finally: fp.close()
    
def GetScriptCases(filename):
    '''
    parm: script dir
    return: a list include class name at position of 0
    '''
    fp = open(filename, 'r+')
    cases = []
    t = re.compile(r'class\ (.*)\(unittest\.TestCase\)\s*:')
    p = re.compile(r'\s{4}def\s+(test.*)\(self\)\s*:')
    try:
        
        for line in fp.readlines():
            tt = t.match(line)
            if tt:
                cases.append(tt.group(1))
                continue
            m = p.match(line)
            if m:
                cases.append(m.group(1))
        fp.close()
        return cases
    except IOError:
        fp.close()
        raise IOError
    finally: fp.close()
    
#print GetScriptCases('/home/liujian/code/s250/testcases/ResetMountDisk.py')
#KillRunningScript('TV_temp.py', 'list_test', 'list_test')


def onRun():
    def onStatus(arg):
        if arg == 'yes':
            print 'yes'
        elif arg =='no':
            print 'no'
    onStatus('yes')

onRun()