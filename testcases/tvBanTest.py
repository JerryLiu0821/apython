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
        self.a.input.back(3)


    def tearDown(self):
        pass

    def test2DTV(self):
        """2D点播视频暂停,播放,seek,声音大小调节功能测试|点播2D视频，进行操作"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#test2DTV"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n test2DTV")
            self.fail("Error happened: %s %s" % (self.error, e))

    def test3DTV(self):
        """3D点播视频暂停,播放,seek,声音大小调节功能测试|点播3D视频，进行操作"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#test3DTV"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n test3DTV")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testResolution3D(self):
        """切换3D视频分辨率|3D频道清晰度切换"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testResolution3D"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testResolution3D")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testScale3D(self):
        """切换3D视频画面比例|3D频道画面比例切换"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testScale3D"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testScale3D")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testExit3DPlay(self):
        '''3D频道播放退出|1.播放3D频道 2.退出播放 3.播放2D频道'''
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testExit3DPlay"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testExit3DPlay")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testDolbyPlay(self):
        '''杜比点播视频暂停,播放,seek,声音大小调节功能测试|点播杜比视频，进行操作'''
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testDolbyPlay"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testDolbyPlay")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testResolutionDolby(self):
        """切换杜比视频分辨率|杜比频道清晰度切换"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testResolutionDolby"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testResolutionDolby")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testScaleDolby(self):
        """切换杜比视频画面比例|杜比频道画面比例切换"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testScaleDolby"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testScaleDolby")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testResolutionMusic(self):
        """切换音乐视频分辨率|音乐频道清晰度切换"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testResolutionMusic"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testResolutionMusic")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testPlayRecord(self):
        """TV版播放记录播放|通过播放记录进入TV版播放视频"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testPlayRecord"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testPlayRecord")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testSearchPlay(self):
        """TV版搜索视频播放|使用乐搜播放视频"""
        #self.jar = "uiautomatortest.jar"
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testSearchPlay"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testSearchPlay")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
