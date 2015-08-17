# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2014

@author: liujian
'''
import unittest
import Stability
import time, re
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class TestDesktop(unittest.TestCase):


    def setUp(self):
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.id = self.setup.device_id
        self.error = ''
        self.a.input.back(3)


    def tearDown(self):
        pass


    def _testDesktopSwitch(self):
        """桌面切换|关闭桌面视频，在轮播频道和搜索之间切换"""
        try:
            anr = 0
            self.operateDesktopStyle(1, 'close')
            self.launchLetv()
            for i in range(5):
                self.a.input.left()
                time.sleep(2)
                self.a.input.right()
                time.sleep(5)
                if not self.isPlaying():
                    anr += 1
            self.a.log.debug("", "raise self.failureException('直播桌面和搜索切换5次出现ANR次数: %s 次')" %anr)
            if anr > 0:
                raise Exception
            self.operateDesktopStyle(1,'open')
        except Exception, e :
            self.operateDesktopStyle(1,'open')
            self.a.log.debug("", "\n testDesktopSwitch")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testSwitchLiveAndSearch(self):
        """直播和搜索切换|关闭视频桌面在直播和搜索之间切换"""
        self.jar = "uiautomatortest.jar"
        self.case = "com.letv.uiautomator.Desktop#testSwitchLiveAndSearch"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testSwitchLiveAndSearch")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testSwitchFiveScreen(self):
        """主页键切换桌面|关闭视频桌面按主页键切换桌面"""
        self.jar = "uiautomatortest.jar"
        self.case = "com.letv.uiautomator.Desktop#testSwtichFiveScreen"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testSwitchLiveAndSearch")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    
    def launchLetv(self):
        self.a.device.sh('input keyevent 4401')
        time.sleep(10)
        self.a.input.right()
        time.sleep(2)
        self.a.input.right()
        time.sleep(5)
    
    def operateDesktopStyle(self,position, opt):
        """default is open, closed after change"""
        self.a.device.sh("input keyevent 176")
        time.sleep(2)
        self.a.input.left(8)
        self.a.input.down()
        self.a.input.right()
        self.a.input.center()
        time.sleep(2)
        self.a.input.up(4)
        #\u901a\u7528\u7248 通用版  
        #\u6781\u901f\u7248 极速版
        #\u5f00\u542f 开启  
        #\u5173\u95ed 关闭
        #\u8f6e\u64ad\u9891\u9053 轮播频道
        #\u4fe1\u53f7\u8f93\u5165 信号源输入
        self.a.input.down(position -1 )
        default = ''
        if position == 1 or position == 3:
            default = u'\u5f00\u542f'
        elif position == 2:
            default = u'\u8f6e\u64ad\u9891\u9053'
        elif position == 4:
            default = u'\u901a\u7528\u7248'
           
        w = self.a.ui.screen()
        if opt == 'open':
            if default not in w.texts()[position*2-1]:
                print 'open'
                self.a.input.center()
                time.sleep(1)
        elif opt == 'close':
            if default in w.texts()[position*2-1]:
                print 'close'
                self.a.input.center()
                time.sleep(1)
        else:
            self.error = 'cannot open settings'
            raise Exception
                
    
    def isPlaying(self):
        try:
            time.sleep(2)
            w = self.a.ui.waitfor( anyof = [
                                            self.a.ui.widgetspec(id='message')       
                                            ]).id()
            if w == 'message':
                self.a.input.left(2)
                self.a.input.center()
                self.error=' Force close happened.'
                return False
        except:
            return True
            


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
