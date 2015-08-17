# -*- coding: utf-8 -*-
'''
Created on Aug 4, 2014

@author: ZhaoJianning
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
        #self.a.input.back(3)


    def tearDown(self):
        pass

    def testSeekMedia(self):
        """压力测试：播放视频或音频，对视频/音频做seek操作|对视频/音频做seek操作"""
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testSeekMedia"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testSeekMedia")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testPlayPauseMedia(self):
        """压力测试：播放视频或音频，对视频/音频做play/pause操作|对视频/音频做play/pause操作"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testPlayPauseMedia"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testPlayPauseMedia")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testVodScaleChange(self):
        """压力测试：播放点播视频，对点播视频做更改画面比例操作|对点播视频做更改画面比例操作"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testVodScaleChange"
        self.count = "count"
        self.times = "1000"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case, self.count, self.times)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testVodScaleChange")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testVodResolutionChange(self):
        """压力测试：播放点播视频，对点播视频做更改清晰度操作|对点播视频做更改清晰度操作"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testVodResolutionChange"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testVodResolutionChange")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testLiveScaleChange(self):
        """压力测试：播放轮播台视频，对轮播视频做更改画面比例操作|对轮播视频做更改画面比例操作"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testLiveScaleChange"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testLiveScaleChange")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testLiveResolutionChange(self):
        """压力测试:播放轮播台视频，对轮播视频做更改清晰度操作|对轮播视频做更改清晰度操作"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testLiveResolutionChange"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testLiveResolutionChange")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testChangeChannel(self):
        '''压力测试：直播台频道切换|直播台频道切换'''
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testChangeChannel"
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
