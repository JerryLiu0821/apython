import os
import re

def getFiles(wantdir):
    paths = []
    for root,folder,files in os.walk(wantdir):
        for f in files:
            if os.path.splitext(f)[1] == '.java':
                paths.append(os.path.join(root,f))
    return paths

def testCaseParse(filename):
    dicts = {}
    # t = re.compile(r'\s*public\s+class\s+(\w+)\s+extends\s+BaseCase\s*{\s*')
    p = re.compile(r'\s*public\s+void\s+(test.*)\(\)\s+.*\s*{\s*')
    classname = filename.split('src')[1].split(".")[0].replace("/", ".")[1:]
    print ""
    with open(filename,"r+") as fp:
        for line in fp:
            for line in fp:
                rp = p.match(line)
                if rp:
                    testname = rp.group(1)
                    print classname+"#"+testname

def convert(srcpath):
    build = re.compile(r'<project name=\"(.*)\" default=\"build\">')
    with open(os.path.join(srcpath, "build.xml"), "r") as fp:
        for line in fp:
            m = build.match(line)
            if m:
                print m.group(1)+".jar"
                break
    for src in getFiles(srcpath):
        testCaseParse(src)



if __name__ == '__main__':
    convert(".")
