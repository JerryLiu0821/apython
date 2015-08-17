# -*- coding: utf-8 -*-
'''
Created on Jun. 17, 2014

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

class TestSwitchScreen(unittest.TestCase):


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
            #self.fail("Error happened: %s" %self.error)

    def tearDown(self):
        self.a.input.back(3)
    
    def getMemInfo(self):
        print android.log.report_directory()
        Stability.takeMeminfo(self.id, android.log.report_directory()).meminfo()
        #time.sleep(300)
        
    def testSwitchScreen(self):
        '''Tuner信号源下进行多屏切换|信号源连接Tuner，左右切换大屏'''
        try :
            for i in range(10):
                print i
                for i in range(15):
                    self.a.input.right()
                for i in range(15):
                    self.a.input.left()
            self.getMemInfo()
            
        except Exception, e :
            self.a.log.debug("", "\n testCaptureMeminfo")
            self.fail(self.error)
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
