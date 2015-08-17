# -*- coding: utf-8 -*-
'''
Created on Aug 4, 2014

@author: ZhaoJianning
'''
import unittest
import time, re, commands
import sys,os, subprocess
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../testcases')
import Stability

class TestUiAutomator(unittest.TestCase):


    def setUp(self):
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.id = self.setup.device_id
        self.error = ''
        self.a.input.back(3)


    def tearDown(self):
        pass
    
    def testAccount(self):
        """乐视会员帐号登陆|乐视会员帐号登陆"""
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testAccount"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n test2DTV")
            self.fail("Error happened: %s %s" % (self.error, e))

    def test2DTV(self):
        """2D点播视频暂停,播放,seek,声音大小调节功能测试|点播2D视频，进行操作"""
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
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
            
    def testResolutionTV(self):
        """更改2D电视剧分辨率|更改2D电视剧分辨率"""
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testResolutionTV"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testResolutionTV")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testScaleTV(self):
        """更改2D电视剧画面比例|更改2D电视剧画面比例"""
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testScaleTV"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testScaleTV")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testMovie(self):
        """电影台点播视频暂停,播放,seek,声音大小调节功能测试|点播电影视频，进行操作"""
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testMovie"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testMovie")
            self.fail("Error happened: %s %s" % (self.error, e))
            
            
    def test4k(self):
        """4k点播视频暂停,播放,seek,声音大小调节功能测试|点播4k视频，进行操作"""
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#test4k"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n test4k")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testResolution4k(self):
        """切换4k视频分辨率|4k频道清晰度切换"""
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testResolution4k"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testResolution1080p")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testScale4k(self):
        """切换4k视频画面比例|4k频道画面比例切换"""
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testScale4k"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testScale4k")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def test1080p(self):
        """1080p点播视频暂停,播放,seek,声音大小调节功能测试|点播1080p视频，进行操作"""
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#test1080p"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n test1080p")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testResolution1080p(self):
        """切换1080p视频分辨率|1080p频道清晰度切换"""
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testResolution1080p"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testResolution1080p")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testScale1080p(self):
        """切换1080p视频画面比例|1080p频道画面比例切换"""
        self.jar = "UiAutomator.jar"
        self.case = "com.letv.tvban.TvTest#testScale1080p"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testScale1080p")
            self.fail("Error happened: %s %s" % (self.error, e))

    def test3DTV(self):
        """3D点播视频暂停,播放,seek,声音大小调节功能测试|点播3D视频，进行操作"""
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
