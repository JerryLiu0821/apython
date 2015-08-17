# -*- coding: utf-8 -*-
'''
Created on Jun. 16, 2014

@author: zhaojianning
'''
import unittest
import Stability
import time, os
import threading
import subprocess
import re
import Stability
import android

class TestIozone(unittest.TestCase):


    def setUp(self):
        try :
            self.error = ''
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.stabdl = Stability.StabDL(self.a)
            self.id = self.setup.device_id  
            self.iozonePath = "../testcases/setup/iozone" 
            self.usbPath = ""
            self.path = "/mnt/sdcard"
            self.a.input.back(3)
        except :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        self.a.input.back(3)
        
    def prepareIozone(self):
        if "No such" not in self.a.device.sh("ls /mnt/sdcard/iozone.xls"):
            self.a.device.sh("rm -rf /mnt/sdcard/iozone.xls")
        cmd1 = "adb -s %s shell chmod 777 /data/iozone" %self.id
        if "No such" in str(subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()):
            print 'push iozone'
            cmd2 = "adb -s %s push %s /data/" %(self.id,self.iozonePath)
            result = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            print 'result is %s' %str(result)
            if "KB" in str(result):
                print 'push successfully'
                #self.a.device.sh(cmd)
                print os.system(cmd1)
                return True
            else:
                return False
        return True
    
    def getStoragePath(self, type):
        print 'get usb path'
        cmd1 = "mount | busybox awk -F ' ' '/\/mnt\/usb\/sd[a-z][0-9]*/{print $3}'"
        cmd2 = "mount | busybox awk -F ' ' '/\/mnt\/usb\/sd[a-z][0-9]*/{print $2}'"
        result1 = self.a.device.sh(cmd1).encode("utf-8").strip().split('\r\n')
        print result1
        for i in range(len(result1)):
            if type in result1[i]:
                self.usbPath = self.a.device.sh(cmd2).encode("utf-8").strip().split('\r\n')[i]
                print self.usbPath
                return True
        return False
            
    def getMemInfo(self):
        while True:
            print android.log.report_directory()
            Stability.takeMeminfo(self.id, android.log.report_directory()).meminfo()
            time.sleep(600)
        
    def testData(self):
        '''data分区读写|系统data分区进行iozone读写'''
        try :
            #t = threading.Thread(target = self.getMemInfo)
            #t.start()
            if not self.prepareIozone():
                self.error = "no iozone tool in data directory"
                raise Exception
            time.sleep(5)
            
            self.jar = "UiAutomator.jar"
            #self.jar = "UiAutomator.jar"
            self.case = "com.letv.system.TestSystem#testData"
            #self.arg = "usb"
            #self.argvalue = self.usbPath
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
            workd = os.path.join(android.log.report_directory(), android.log.logs_directory())
            os.system('adb -s %s pull %s/iozone.log %s' %(self.id,self.path,workd))
            os.system('adb -s %s pull %s/iozone.xls %s' %(self.id,self.path,workd))
            '''
            cmd = "/data/iozone -az -i 0 -i 1 -i 2 -i 6 -i 7 -n 4k -g 1G -I -f /data/iozone.tmp -Rb /mnt/sdcard/iozone.xls -C > /mnt/sdcard/iozone.log"
            print self.a.device.sh(cmd)
            time.sleep(5)
            if "No such" in self.a.device.sh("ls /mnt/sdcard/iozone.xls"):
                self.error = 'failed to run data iozone'
                raise Exception
            '''
        except Exception, e :
            self.a.log.debug("", "\n testData")
            self.fail(self.error)
            
    def testFat(self):
        '''fat分区读写|外接fat分区进行iozone读写'''
        try :
            t = threading.Thread(target = self.getMemInfo)
            t.start()
            if not self.prepareIozone():
                self.error = "no iozone tool in data directory"
                raise Exception
            print 'set up iozone successfully'
            if not self.getStoragePath("vfat"):
                self.error = "failed to find the fat usb device"
                raise Exception
            time.sleep(5)
            
            self.jar = "UiAutomator.jar"
            #self.jar = "UiAutomator.jar"
            self.case = "com.letv.system.TestSystem#testFat"
            self.arg = "usb"
            self.argvalue = self.usbPath
            ua = Stability.UiAutomator(self.id, self.jar, self.case, self.arg, self.argvalue)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
            workd = os.path.join(android.log.report_directory(), android.log.logs_directory())
            os.system('adb -s %s pull %s/iozone.log %s' %(self.id,self.path,workd))
            os.system('adb -s %s pull %s/iozone.xls %s' %(self.id,self.path,workd))
            '''
            cmd = "/data/iozone -a -i 0 -i 1 -i 2 -i 6 -i 7 -n 4k -g 4G -f %s/iozone.tmp -Rb /mnt/sdcard/iozone.xls -C > /mnt/sdcard/iozone.log" %self.usbPath
            print self.a.device.sh(cmd)
            time.sleep(5)
            if "No such" in self.a.device.sh("ls /mnt/sdcard/iozone.xls"):
                self.error = 'failed to run data iozone'
                raise Exception
            '''
        except Exception, e :
            self.a.log.debug("", "\n testFat")
            self.fail(self.error)
            
    def testNtfs(self):
        '''ntfs分区读写|外接ntfs分区进行iozone读写'''
        try :
            t = threading.Thread(target = self.getMemInfo)
            t.start()
            if not self.prepareIozone():
                self.error = "no iozone tool in data directory"
                raise Exception
            if not self.getStoragePath("ufsd"):
                self.error = "failed to find the fat usb device"
                raise Exception
            time.sleep(5)
            
            self.jar = "UiAutomator.jar"
            #self.jar = "UiAutomator.jar"
            self.case = "com.letv.system.TestSystem#testNtfs"
            self.arg = "usb"
            self.argvalue = self.usbPath
            ua = Stability.UiAutomator(self.id, self.jar, self.case, self.arg, self.argvalue)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
            workd = os.path.join(android.log.report_directory(), android.log.logs_directory())
            os.system('adb -s %s pull %s/iozone.log %s' %(self.id,self.path,workd))
            os.system('adb -s %s pull %s/iozone.xls %s' %(self.id,self.path,workd))
            '''
            cmd = "/data/iozone -a -i 0 -i 1 -i 2 -i 6 -i 7 -n 4k -g 4G -f %s/iozone.tmp -Rb /mnt/sdcard/iozone.xls -C > /mnt/sdcard/iozone.log" %self.usbPath
            print self.a.device.sh(cmd)
            time.sleep(5)
            if "No such" in self.a.device.sh("ls /mnt/sdcard/iozone.xls"):
                self.error = 'failed to run data iozone'
                raise Exception
            '''
        except Exception, e :
            self.a.log.debug("", "\n testNtfs")
            self.fail(self.error)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
