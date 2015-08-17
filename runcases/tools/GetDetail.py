'''
Created on Apr 16, 2014

@author: liujian
'''

import sys,os,commands
from Unpack import *

from XMLParser import *
reload(sys) 
sys.setdefaultencoding('utf8') 

def getApkDetail(apkFileOrDir):
    manifest = 'AndroidManifest.xml'
    AXMLPrinter2 = './AXMLPrinter2.jar'
    #directory
    dicts = {}
    if os.path.isdir(apkFileOrDir):
        for root,dirs,files in os.walk(apkFileOrDir):
            for f in files:
                if cmp(os.path.splitext(f)[1], '.apk') == 0:
                    apkFile = os.path.join(root,f)
                    unpackDir = os.path.join(root,'unpack')
                    unzip_file_into_dir(apkFile, unpackDir)
                    status,output=commands.getstatusoutput('java -jar %s %s' %(AXMLPrinter2, os.path.join(unpackDir,manifest)))
                    pkg, hwacc = XMLHandler().parserXML(output)
                    dicts[f] = hwacc
    #apk file                
    elif os.path.isfile(apkFileOrDir):
        unpackDir = os.path.join(os.path.splitext(apkFileOrDir)[0]+"-unpanck")
        unzip_file_into_dir(apkFileOrDir, unpackDir)
        status,output=commands.getstatusoutput('java -jar %s %s' %(AXMLPrinter2, os.path.join(unpackDir,manifest)))
        pkg, hwacc = XMLHandler().parserXML(output)
        dicts[apkFileOrDir] = hwacc
        
    for key in dicts.keys():
        print key, dicts[key]

def crashInLogcat(logFileOrDir):
    ANR = 'ANR in'
    FATAL = 'FATAL EXCEPTION'
    TOMBSTONE = 'Build fingerprint'
    anr = []
    fatal = []
    tombstone = []
    
    def getCrash(f):
        fp = open(f,'rt')
        try:
            for line in fp.readlines():
                line = os.path.join(f,line)
                line = line.rstrip()
                if ANR in line:
                    anr.append(line)
                elif FATAL in line:
                    fatal.append(line)
                elif TOMBSTONE in line:
                    tombstone.append(line)
                else:
                    pass
            fp.close()
        except IOError:
            #print IOError
            print 'fail to open %s'%f
            fp.close()
        finally:fp.close()
    #directory
    if os.path.isdir(logFileOrDir):
        for root,dirs,files in os.walk(logFileOrDir):
            for f in files:
                filename = os.path.join(root,f)
                getCrash(filename)
                
    #logcat
    elif os.path.isfile(logFileOrDir):
        getCrash(logFileOrDir)
    else:
        pass
    
    
    print '==> ANR: %s <==' %len(anr)
    for a in anr:
        print a
    print '==> FATAL EXCEPTION: %s <==' %len(fatal)
    for f in fatal:
        print f
    print '==> TOMBSTONES: %s <==' %len(tombstone)
    for t in tombstone:
        print t
            
def showUsage():
    print u'Usage:  python GetDetail.py <option> <file-path or directory> \r\n\toption:\r\n\
    \t\t -H : show usage\r\n\
    \t\t -A : get hardwareAccelerated value in apk \r\n\
    \t\t -L : find crash in logcat \r\n\
    \t\t -P : make a panel for procrank file\r\n\
    \t\t -M : make a panel for dumpsys meminfo file\r\n\
    '
    
def main():
    if len(sys.argv) != 3:
        showUsage()
        return 2
    
    type = sys.argv[1]
    fileOrDir = unicode(sys.argv[2],'utf-8')
    if not os.path.exists(fileOrDir):
        print 'Error: file or directory is not exist!!'
        showUsage()
        return 2
    if type == '-A':
        getApkDetail(fileOrDir)
    elif type == '-L':
        crashInLogcat(fileOrDir)
    elif type == '-P':
        status,output = commands.getstatusoutput('python procrank.py '+fileOrDir)
        print output
        if status:
            showUsage()
    elif type == '-M':
        status,output = commands.getstatusoutput('python dumpsysMeminfo.py '+fileOrDir)
        print output
        if status:
            showUsage()
    else:
        showUsage()
    
if __name__ == '__main__':
    main()
    