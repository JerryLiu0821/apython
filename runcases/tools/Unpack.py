# --*-- encoding:utf-8 --*--
'''
Created on Apr 16, 2014

@author: liujian
'''

import os, commands, zipfile

def unzip_file_into_dir(file, dir):
    
    if os.path.exists(dir):
        status, output = commands.getstatusoutput('rm -rf ' + dir)
    
    try:
        os.mkdir(dir,'0775')
        zfobj = zipfile.ZipFile(file)
        
        for name in zfobj.namelist():
            path = os.path.join(dir,name)
            
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path),0777)
    
            if cmp(name, 'res') == 0:
                path = path + '_rename'
            
            if os.path.isdir(path) == False:
                outfile = open(path, 'wb')
                outfile.write(zfobj.read(name))
                outfile.close()
    
        zfobj.close()

    except:
        status,output = commands.getstatusoutput('/usr/bin/unzip %s -d %s' %(file,dir))
        
        if status != 0:
            return False
    
    return True

if __name__=='__main__':
    unzip_file_into_dir('T2Launcher.apk', './test')