# -*- coding: utf-8 -*-
'''
Created on Nov 21, 2013

@author: liujian
'''
import unittest
import time, os
import threading
import subprocess
import re, commands
import sys
sys.path.append('../testcases')
import Stability

class TestReboot(unittest.TestCase):


    def setUp(self):
        try :
            self.error = ''
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.stabdl = Stability.StabDL(self.a)
            self.id = self.setup.device_id   
            self.a.input.back(3)
        except :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        self.a.input.back(3)

    def connect(self):
        for i in range(1, 15):
            print '%s connect' %i
            os.system ('adb disconnect ' + self.id)
            time.sleep(1)
            os.system('adb connect ' + self.id)
            time.sleep(1)
            getprop = subprocess.Popen('adb -s %s shell getprop | grep version' %self.id, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            print getprop 
            if 'device not found' not in str(getprop):
                print 'connected to device ' + self.id
                os.system("adb -s %s root" %self.id)
                time.sleep(3)
                os.system('adb connect ' + self.id)
                return True
            time.sleep(10)
        return False
            
    def rebootDevice(self):
        self.a.device.sh('su -c reboot reboot')

    def testReboot(self):
        '''adb重启|adb反复重启'''
        try :
            t = threading.Thread(target = self.rebootDevice)
            t.start()
            time.sleep(180)
            print "connect"
            if not self.connect():
                self.error = 'cannot connect to device'
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testReboot")
            self.fail(self.error)

    def _testRebootAd(self):
        '''开关广告倒计时|'''
        try :
            t = threading.Thread(target = self.rebootDevice)
            t.start()
            time.sleep(90)
            print "connect"
            if not self.connect():
                self.error = 'cannot connect to device'
                raise Exception
            ad=self.a.device.sh('grep "tvos    : ShowBootVideoTime :0" /data/Logs/Log.0/*')
            if ad =='':
                print 'ad is not successfully'
                self.error = 'ad is not successfully'
                raise Exception
            else:
                print 'ad is successfully'
        except Exception, e :
            self.a.log.debug("", "\n testReboot")
            self.fail(self.error)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
