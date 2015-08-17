# -*- coding: utf-8 -*-
'''
Created on Jun. 16, 2014

@author: zhaojianning
'''
import unittest
import time, os
import threading
import subprocess
import re,sys
import android
import serial
sys.path.append('../testcases')
import Stability

class TestStressApp(unittest.TestCase):


    def setUp(self):
        try :
            self.error = ''
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.stabdl = Stability.StabDL(self.a)
            self.id = self.setup.device_id  
            self.stressAppPath = "../testcases/setup/stressapptest" 
            self.usbPath = ""
            #self.a.input.back(3)
            print "serial connection"
            self.ser = ''
            self.ser = serial.Serial(port='/dev/ttyUSB1', baudrate=115200, timeout=0)
            if  not self.ser.isOpen():
                self.error = 'cannot open %s' % self.ser.port
                raise Exception
        except :
            #self.a.log.debug("", "\n Set up")
            self.fail("Error happened: %s" %self.error)

    def tearDown(self):
        pass
        #self.a.input.back(3)
        
    def prepareStressApp(self):
        cmd1 = "adb -s %s shell chmod 755 /system/bin/stressapptest" %self.id
        if "No such" in str(subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()):
            print 'push stressapptest'
            os.system("adb -s %s remount" %self.id)
            cmd2 = "adb -s %s push %s /system/bin/" %(self.id,self.stressAppPath)
            result = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            print 'result is %s' %str(result)
            if "KB" in str(result):
                print 'push successfully'
                time.sleep(5)
                os.system('adb -s %s remount' %self.id)
                #self.a.device.sh(cmd)
                print os.system(cmd1)
                print 'change mode successfully'
                return True
            else:
                return False
        return True
    
    def sendCommand(self, command):
        self.ser.write(command+'\n')
            
    def getMemInfo(self):
        while True:
            print android.log.report_directory()
            Stability.takeMeminfo(self.id, android.log.report_directory()).meminfo()
            time.sleep(600)
        
    def testStressApp(self):
        '''连接串口进行内存压力测试|stressapptest内存压力测试 请确保串口号为/dev/ttyUSB1, 权限为777'''
        try :
            #t = threading.Thread(target = self.getMemInfo)
            #t.start()
            if not self.prepareStressApp():
                self.error = "no stressapptest tool in directory"
                raise Exception
            time.sleep(5)
            print "begin to execute stress test"
            cmd = "stressapptest -s 43200 -M 300 -m 8 -i 8 -v 13 > /mnt/sdcard/stresslog&"
            #cmd1 = "busybox nice -n -10 stressapptest"
            #cmd2 = "adb -s %s shell stressapptest -s 43200 -M 300 -m 8 -i 8 -v 13 > %s/stress.log" %(self.id, android.log.report_directory())
            #self.a.device.sh(cmd1)
            #time.sleep(3)
            #print os.system(cmd2)
            self.sendCommand(cmd)
            time.sleep(5)
            if "No such" in self.a.device.sh("ls /mnt/sdcard/stresslog"):
                self.error = 'failed to run stressapptest'
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testStressApp")
            self.fail(self.error)
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
