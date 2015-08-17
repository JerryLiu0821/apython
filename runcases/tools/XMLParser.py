
'''
Created on Apr 16, 2014

@author: liujian
'''
import StringIO
import xml.sax
import sys
from xml.sax.handler import *

import commands

class XMLHandler(ContentHandler):
    def __init__(self):
        self.hardwareAccelerated = ''
        self.package = ''
        
    def startDocument(self):
        pass
    def enDocument(self):
        pass
    
    def startElement(self,name, attrs):
        if name == 'manifest':
            self.package = attrs.get('package')
        if name == 'application':
            self.hardwareAccelerated = attrs.get('android:hardwareAccelerated')
            
    def parserXML(self,xmlStr):
        parser = xml.sax.make_parser()
        handler = XMLHandler()
        parser.setContentHandler(handler)
        parser.parse(StringIO.StringIO(xmlStr))
        return handler.package,handler.hardwareAccelerated
        

if __name__ == '__main__':
    status,output = commands.getstatusoutput('java -jar /home/liujian/s250/apk_py_src/AXMLPrinter2.jar /home/liujian/s250/apk_py_src/launcher/AndroidManifest.xml')
    h = XMLHandler()
    print h.parserXML(output)
