# -*- coding: utf-8 -*-
import android, unittest, time, sys, traceback
import inspect
from random import choice

import runtests
import re, os, random,sys
sys.path.append('../testcases')
import Stability



class testLivePlay(unittest.TestCase):
    """Live_Play """

    def setUp(self):
        try :
            #self.playtime = 1*60*60 # play 'playtime' seconds for each video
            self.playtime = 2
            self.temPlaytime = 2
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.error=''
            self.stabdl=Stability.StabDL(self.a)
            self.id = self.setup.device_id 
            self.a.input.back(3)
        except Exception, e :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        self.a.input.back(3)
    
    def testChangeLiveAndUrl(self):
        """直播台和URL互切|在直播界面启动点播URL"""
        try:
            self.urls = ['http://10.204.8.236:8080/live/1080p/a.m3u8',
                        'http://10.204.8.236:8080/live/4k/a.m3u8',
                        'http://10.204.8.236:8080/live/720p/a.m3u8',
                        'http://10.204.8.236:8080/live/bq/a.m3u8',
                        'http://10.204.8.236:8080/live/cq/a.m3u8',
                        'http://10.204.8.236:8080/live/gq/a.m3u8',]
            self.launchLetv()
            time.sleep(2)
            times = 0
            for i in range(len(self.urls)*1):
                if i >= len(self.urls):
                    times = len(self.urls)*1 -i -1 
                else:
                    times = i
                self.a.input.back()
                time.sleep(2)
                self.a.device.sh("input keyevent 166")
                time.sleep(20)
                cmd = "am start -a android.intent.action.VIEW -d \'%s\' -n com.letv.videoplayer/.MainActivity" % self.urls[times]
                print 'playing %s' %self.urls[times]
                self.a.device.sh(cmd)
                time.sleep(10)
                if not self.isPlaying():
                    raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testChangeLiveAndUrl")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def _testChangeLetvDisplay(self):
        """切换直播台的清晰度|进入乐视直播台菜单，切换清晰度"""
        try:
            self.a.input.home()
            self.launchLetv() 
            time.sleep(5)
            self.a.input.menu()
            time.sleep(2)
            self.a.input.up()
            self.a.input.right(2)
            self.a.input.center()
            time.sleep(2)
            w = self.a.ui.screen()
            if 'displaySwitcher' not in w.ids():
                self.error = 'cannot open menu in letv live screen'
                runtests.log_screenshot(self.a, '', 'fail_open_menu', 'Liveplay')
                raise Exception
            self.a.input.down(2)
            for i in range(3):
                self.a.input.center()
                time.sleep(5)
                if not self.isPlaying():
                    runtests.log_screenshot(self.a, '', 'change_display_fail', 'Liveplay')
                    raise Exception
                else:pass
        except Exception, e :
            self.a.log.debug("", "\n testChangeLetvDisplay")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    def _testChangeLetvScreenRate(self):        
        """切换直播台的画面比例|进入乐视直播台菜单，切换画面比例"""
        try:
            self.launchLetv() 
            time.sleep(4)
            self.a.input.menu()
            time.sleep(2)
            self.a.input.up()
            self.a.input.right(2)
            self.a.input.center()
            time.sleep(2)
            w = self.a.ui.screen()
            if 'displaySwitcher' not in w.ids():
                self.error = 'cannot open menu in letv live screen'
                runtests.log_screenshot(self.a, '', 'fail_open_menu', 'Liveplay')
                raise Exception
            self.a.input.up(2)
            self.a.input.down()
            time.sleep(2)
            for i in range(3):
                self.a.input.center()
                time.sleep(5)
                if not self.isPlaying():
                    raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testStabLetvUpToDownSomeChannel")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    def testChangeLiveChannelByKey(self):
        """数字切换直播频道| 按数字键切换直播频道"""
        try:
            self.launchLetv()
            for i in range(10):
                number = random.randint(0,100);
                if not self.pressChannelNumber(number):
                    raise Exception
        except Exception ,e:
            self.a.log.debug("", "\n testChangeLiveChannelByKey")
            self.fail("Error happened: %s %s" % ( self.error, e))
          
    def testChangLiveChannelByChannelDownKey(self):
        """直播台向下切换 | 直播台向下列表遍历，直播台向下切换"""
        try:
            self.launchLetv() 
            self.changeLiveChannelByDirection(3, 'down', 10)

        except Exception, e :
            self.a.log.debug("", "\n testChangLiveChannelByChannelupKey")
            self.fail("Error happened: %s %s" % ( self.error, e))

    def testChangLiveChannelByChannelUpKey(self):
        """直播台向上切换 | 直播台向上列表遍历，直播台向上切换"""
        try:
            self.launchLetv() 
            self.changeLiveChannelByDirection(3, 'up', 10)

        except Exception, e :
            self.a.log.debug("", "\n testChangLiveChannelByChannelUpKey")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    def _testCloseLiveDesktop(self):     
        """关闭直播桌面切换|关闭直播桌面，在直播桌面和废纸波桌面之间切换"""
        try:
            self.operateDesktopStyle(1, 'close')
            self.launchLetv() 
            
            #search to live
            self.a.input.left()
            time.sleep(2)
            self.a.input.right()
            time.sleep(10)
            if not self.isPlaying():
                self.error += ' after change search to live'
                raise Exception
            #live to app
            self.a.input.right()
            time.sleep(2)
            self.a.input.left()
            time.sleep(10)
            if not self.isPlaying():
                self.error += ' after change app to live'
                raise Exception
            
            self.operateDesktopStyle(1, 'open')
        except Exception, e :
            self.operateDesktopStyle(1, 'open')
            self.a.log.debug("", "\n testCloseLiveDesktop")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    def _testCloseLiveDesktopPressHome(self):
        """关闭视频桌面切换主页|从各个界面按主页键切换到直播界面"""
        try:
            self.operateDesktopStyle(1, 'close')
            time.sleep(2)
            self.launchLetv()
            for i in range(1, 6):
                self.a.input.home()
                time.sleep(2)
                self.a.input.right(i)
                time.sleep(1)
                self.a.input.center()
                time.sleep(5)
                self.a.input.home()
                time.sleep(2)
                self.a.input.left(i)
                self.a.input.center()
                time.sleep(10)
                if not self.isPlaying():
                    raise Exception
            self.operateDesktopStyle(1, 'open')
        except Exception, e :
            self.operateDesktopStyle(1, 'open')
            self.a.log.debug("", "\n testCloseLiveDesktopPressHome")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
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
    
    def launchLetv(self):
        self.a.device.sh('input keyevent 4401')
        time.sleep(5)
        self.a.input.right()
        time.sleep(2)
        self.a.input.right()
        time.sleep(2)
    
    
    def pressChannelNumber(self, number):
        print 'press key %s' %number
        try:
            f = number / 10
            d = number % 10
            if f == 0:
                self.a.device.sh('input keyevent %s' %(d+7))
                time.sleep(3)
            elif f < 10:
                self.a.device.sh("input keyevent %s" %(f+7))
                time.sleep(0.1)
                self.a.device.sh("input keyevent %s" %(d+7))
                time.sleep(3)
            elif f < 100:
                m = f / 10
                md = f % 10
                self.a.device.sh("input keyevent %s" %(m+7))
                time.sleep(0.1)
                self.a.device.sh("input keyevent %s" %(md+7))
                time.sleep(0.1)
                self.a.device.sh("input keyevent %s" %(d+7))
                time.sleep(3)
            else:
                pass
            time.sleep(5)
            if not self.isPlaying():
                return False
            else:
                return True

        except Exception, e:
            return False
    
    def changeLiveChannelByDirection(self,times, direction, playtimes):
        if direction == 'up':
            for i in range(times):
                self.a.input.channel_up()
                time.sleep(playtimes)
                #if not self.isPlaying():
                    #raise Exception
        elif direction == 'down':
            for i in range(times):
                self.a.input.channel_down()
                time.sleep(playtimes)
                #if not self.isPlaying():
                    #raise Exception
        else:
            self.error = 'input error'
            raise Exception
        
    def isPlaying(self):
        try:
            print 'checking'
            time.sleep(5)
            w = self.a.ui.waitfor( anyof = [
                                            self.a.ui.widgetspec(id = 'tv_loading'),
                                            self.a.ui.widgetspec(id='message')       
                                            ]).id()
            if w == 'message':
                self.a.input.down()
                self.a.input.center()
                self.error=' Force close happened.'
                return False
            if w == 'tv_loading':
                self.error='tv is loading.'
                return False
        except:
            return True 

    
if __name__ == '__main__':
    unittest.main()


