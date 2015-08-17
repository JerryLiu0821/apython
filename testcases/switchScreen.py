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
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testChangeDesktop"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testSwitchScreen")
            self.fail("Error happened: %s %s" % (self.error, e))
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
