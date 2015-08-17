# -*- coding: utf-8 -*-
'''
Created on Jun. 17, 2014

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
import serial

class TestVolumeChange(unittest.TestCase):


    def setUp(self):
        try :
            self.error = ''
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.stabdl = Stability.StabDL(self.a)
            self.id = self.setup.device_id  
            #self.a.input.back(3)
        except :
            self.a.log.debug("", "\n Set up")
            #self.fail("Error happened: %s" %self.error)

    def tearDown(self):
        pass
        #self.a.input.back(3)
        
    def volumeChange(self):
        self.getMemInfo()
        for i in range(10):
            print i
            for i in range(2):
                self.a.input.volume_up(5)
                time.sleep(1)
            for i in range(2):
                self.a.input.volume_down(5)
                time.sleep(1)
    
    def getMemInfo(self):
        print android.log.report_directory()
        Stability.takeMeminfo(self.id, android.log.report_directory()).meminfo()
        #time.sleep(300)
        
    def testVolumeChange(self):
        '''改变音量测试|不停做音量加减'''
        try :
            self.volumeChange()
            
        except Exception, e :
            self.a.log.debug("", "\n testVolumeChange")
            self.fail(self.error)
            
    def testVolumeInSignal(self):
        '''信号源界面改变音量测试|信号源界面不停做音量加减'''
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.signalSource.VolumeChange"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testVolumeInSignal")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testVolumeInLive(self):
        '''直播台界面改变音量测试|直播台界面不停做音量加减'''
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.liveTV.VolumeChange"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testVolumeInLive")
            self.fail("Error happened: %s %s" % (self.error, e))
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
