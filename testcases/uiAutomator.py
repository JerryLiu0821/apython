# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2014

@author: liujian
'''
import unittest
import Stability
import time, re, commands
import sys,os, subprocess
reload(sys)
sys.setdefaultencoding('utf8')

class TestUiAutomator(unittest.TestCase):


    def setUp(self):
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.id = self.setup.device_id
        self.error = ''
        self.a.input.back(3)


    def tearDown(self):
        pass

    def testNetworkSpeed(self):
        """网络测速|设置中进行网络测速"""
        self.jar = "uiautomatortest.jar"
        self.case = "com.letv.uiautomator.Settings#testNetworkSpeed"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            self.a.log.debug("", "raise self.failureException('网络测速: %s ')" %info[0] )
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testDesktopSwitch")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testPlayAllVideoInUsb(self):
        """播放所有格式的视频|播放U盘中指定的所有视频 """
        self.jar = "uiautomatortest.jar"
        self.case = "com.letv.uiautomator.MultiMedia#testPlayAllLocalMeida"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testPlayAllVideoInUsb")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testLiveScreenRate(self):
        """切换直播画面比例|切换直播台的三种画面比例"""
        self.jar = "uiautomatortest.jar"
        self.case = "com.letv.uiautomator.MultiMedia#testLiveChangeScreenRate"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testLiveScreenRate")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testLiveDisplay(self):
        """切换直播清晰度|切换直播台的各种清晰度"""
        self.jar = "uiautomatortest.jar"
        self.case = "com.letv.uiautomator.MultiMedia#testLiveChangeDisplay"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testLiveDisplay")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
