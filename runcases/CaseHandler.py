# -*- coding: utf-8 -*-
import os,sys, re
import threading, subprocess

class run_case(threading.Thread):    
    def __init__(self, id, list_file, log_dir):
        threading.Thread.__init__(self)
        self.id = id     
        self.config_file = 'TV_temp.py'
        self.list_file = os.path.join('List', list_file)    
        self.log_dir = log_dir 
         
    def run(self):
        if os.name == 'posix':    
            settings_delimeter = ':'     
        else:    
            settings_delimeter = ';'     
        runtests = os.path.join('..','testcases', 'interface','runtests.py')    
        rack_settings = 'stabrackSettings.py'     
        custom_type = 'Custom' 
        print ('python %s --settings %s%s%s --rack-type 1 --custom-type %s  \
            --report-parent-dir %s --run %s' % (runtests,self.config_file, settings_delimeter, rack_settings,custom_type, self.log_dir, self.list_file)) 
        os.system ('python %s --settings %s%s%s --rack-type 1 --custom-type %s  \
            --report-parent-dir %s --run %s' % (runtests,self.config_file, settings_delimeter, rack_settings,custom_type, self.log_dir, self.list_file))
    
    def killRunningScript(self):
        stdout,stderr = self.__shell('ps -aux | grep python')
        stdout = stdout.split(os.linesep)

        user = os.environ['USER']
        pattern = re.compile(r'.*%s\s+(\d+)\s+.*\d+\s+(python.*runtests\.py\s+--settings\s+%s.*%s\s+--run\s+%s)' %(user, self.config_file,self.log_dir,self.list_file))
        pid = []
        pname = ''
        for p in stdout:
            m = pattern.match(p)
            if m:
                pid.append(m.group(1))
                pname = m.group(2)
                break
        if pid != []:
            for x in pid:
            
                print 'kill process '+ x +": "+pname
                o,e = self.__shell('kill -9 '+x)
                return True
        else:
            print 'cannot get process pid'
            return False

    def __shell(self,cmd):
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True).communicate()

class AdbException(Exception):
    """docstring for AdbException"""
    def __init__(self, message):
        Exception.__init__(self,message)

        

class RecordReplay(threading.Thread):
    """docstring for RecordReplay"""
    def __init__(self, tid):
        self.tid = tid

    def __shell(self,cmd):
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True).communicate()        

    def __push(self):
        print self.tid
        o,e = self.__shell('adb -s  %s push ./record  /data/' %self.tid)
        print o, e
        if 'error' in e:
            raise AdbException(e)
        o,e = self.__shell('adb -s %s push ./replay /data/' %self.tid)
        if 'error' in e:
            raise AdbException(e)
        self.__shell('adb -s %s shell chmod 777 /data/record' %self.tid)
        self.__shell('adb -s %s shell chmod 777 /data/replay' %self.tid)

    def record(self):
        self.__push()
        t=threading.Thread(target=lambda:self.__shell('adb -s %s shell ./data/record' %self.tid))
        t.setDaemon(True)
        t.start()

    
    def __stop(self,opt):
        stdout,stderr = self.__shell('ps -aux | grep %s' %opt)
        stdout = stdout.split(os.linesep)
        user = os.environ['USER']
        pattern = re.compile(r'.*%s\s+(\d+)\s+.*\d+\s+(adb\ -s\ %s shell\ \./data/%s)' %(user,self.tid, opt))
        pid = []
        pname = ''
        for p in stdout:
            m = pattern.match(p)
            if m:
                pid.append(m.group(1))
                pname = m.group(2)
                break
        if pid != []:
            for x in pid:
            
                print 'kill process '+ x +": " + pname
                o,e = self.__shell('kill -9 '+x)
                return True
        else:
            print 'cannot get record pid'
            return False

    def stopRecord(self):
            if self.__stop('record'):
                return True
            else:
                return False

    def stopReplay(self):
        if self.__stop('replay'):
            return True
        else:
            return False

    def replay(self):
        t = threading.Thread(target=lambda:self.__shell('adb -s %s shell ./data/replay' %self.tid))
        t.setDaemon(True)
        t.start()



