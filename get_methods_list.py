# -*- coding: utf-8 -*- 

import os, re

def getFiles(wantdir):
    paths = []

    for f in os.listdir(wantdir):
        if os.path.splitext(f)[1] == '.py':
            paths.append(os.path.join(wantdir,f))
    return paths

def parsePyScript(filename):
    title = ''
    dicts = {}
    fp = open(filename, 'r+')
    t = re.compile(r'class\ (.*)\(unittest\.TestCase\)\s*:')
    p = re.compile(r'\s{4}def\s+(test.*)\(self\)\s*:')
    lines = fp.readlines()

    for i in range(len(lines)):
        m = t.match(lines[i])
        if m :
            title = m.group(1)
            break
    for i in range(len(lines)):
        m = p.match(lines[i])
        if m:
            contents = lines[i+1].replace('\r\n','')
            contents = contents.replace(',',' ')
            contents = contents.strip().split("|")[0].rstrip()
            dicts[m.group(1)] = re.subn(r'[\'"]',"",contents)[0].lstrip()
    return title,dicts    

def convertDoc(doc):
    if os.path.exists(doc):
        os.remove(doc)
    fp = open(doc, 'a+')
    fp.write("case说明\tcase名称"+os.linesep)

    for script in getFiles('./testcases/'):
        title, dicts = parsePyScript(script)
        if dicts == {}:
            continue
        for key in dicts:
            fp.write(dicts[key]+"\t")
            fp.write("."+script +':')
            fp.write(title+".")
            fp.write(key)
            fp.write(os.linesep)
    fp.close()

convertDoc('list.txt')
