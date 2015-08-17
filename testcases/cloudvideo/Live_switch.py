# -*- coding: utf-8 -*-
import android, unittest, time, sys, traceback
import inspect
from random import choice

import runtests
import re, os, sys
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
            self.apk = "TTLauncher.apk"
            self.a.input.back(3)
            #self.installLiveAPK()
            #self.launchLetv()
        except Exception, e :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        self.a.input.back(3)
    
          
    def _testChangLiveChannelByChannelupKey(self):
        """ 直播台切换 | 直播台遍历"""
        try:
            self.changLiveChannelByChannelupKey(40, 2)           
        except Exception, e :
            self.a.log.debug("", "\n testStabLetvUpToDownSomeChannel")
            self.fail("Error happened: %s %s" % ( self.error, e))
            
    def installLiveAPK(self):
        os.system("adb -s %s remount" %self.id)
        pushCmd = "adb -s %s push ../testcases/setup/%s /system/app/" %(self.id, self.apk)
        os.system(pushCmd)
        time.sleep(2)
        self.a.device.sh("reboot reboot")
        time.sleep(80)
        os.system("adb disconnect %s" %self.id)
        time.sleep(2)
        os.system("adb connect %s" %self.id)
        time.sleep(2)
        os.system("adb -s %s root" %self.id)
        time.sleep(2)
        os.system("adb connect %s" %self.id)
        
    def launchLetv(self):
        print "launch live tv"
        cmd = "am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n com.ttstv.launcher/com.stv.launcher.T2LauncherActivity -f 0x10200000"
        self.a.device.sh(cmd)
        '''
        for i in range(3):
            self.a.input.home()
            time.sleep(5)
        self.a.input.back(2)
        time.sleep(2)
        for i in range(5):
            if 'com.letv.signalsourcemanager/com.letv.signalsourcemanager.MainActivity' not in str(self.a.ui.window()):
                self.a.input.home()
                time.sleep(2)
                self.a.input.left()
                time.sleep(1)
                self.a.input.center()
            else:
                break
        self.a.input.home()
        time.sleep(2)
        self.a.input.right(2)
        self.a.input.center()
        '''  
    def isPlaying(self):
        try:
            time.sleep(5)
            w = self.a.ui.waitfor( anyof = [
                                            self.a.ui.widgetspec(id = 'tv_loading'),
                                            self.a.ui.widgetspec(id='message', text=re.compile(r'(^Unfortunately.*stopped\.$)'))       
                                            ]).id()
            if w == 'message':
                self.a.input.down()
                self.a.input.center()
                self.error=' Force close happened.'
                return False
            if w == 'tv_loading':
                self.a.log.debug("","Error: This channel can not be played, pls check the network status.")
                self.error='Error: This channel can not be played, pls check network status.'
                return False
        except:
            return True 
    def _testInstallLive(self):
        """安装直播台apk|安装直播台apk"""
        self.installLiveAPK()
        
    def _testLaunchLiveTV(self):
        """打开直播台 | 打开直播台"""
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testLaunchLiveTV"
        try:
            #self.a.device.sh("rm -rf %s/*" %self.path)
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testUSBUpgrade")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testChangeLiveChannel(self):
        """直播台频道键换台 | 直播台频道键换台"""
        #self.launchLetv()
        #time.sleep(5)
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testChangeChannel"
        try:
            #self.a.device.sh("rm -rf %s/*" %self.path)
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testUSBUpgrade")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testChangeLiveChannelInList(self):
        """直播台列表换台 | 直播台列表换台"""
        #self.launchLetv()
        #time.sleep(5)
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testChangeChannelInList"
        try:
            #self.a.device.sh("rm -rf %s/*" %self.path)
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testUSBUpgrade")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testChangeVolume(self):
        """直播台改音量大小 | 直播台改音量大小"""
        #self.launchLetv()
        #time.sleep(5)
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testVolumeChange"
        try:
            #self.a.device.sh("rm -rf %s/*" %self.path)
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testUSBUpgrade")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testChangeResolution(self):
        """直播台改分辨率 | 直播台改分辨率"""
        #self.launchLetv()
        #time.sleep(5)
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testLiveResolutionChange"
        try:
            #self.a.device.sh("rm -rf %s/*" %self.path)
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testUSBUpgrade")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testChangeScale(self):
        """直播台改画面比例 | 直播台改画面比例"""
        #self.launchLetv()
        #time.sleep(5)
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.media.OperationMedia#testLiveScaleChange"
        try:
            #self.a.device.sh("rm -rf %s/*" %self.path)
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testUSBUpgrade")
            self.fail("Error happened: %s %s" % (self.error, e))

    '''
    def changLiveChannelByChannelupKey(self,times, playtimes):
        for i in range(times):
            self.a.input.channel_up()
            time.sleep(playtimes)
            #if not self.isPlaying():
#               raise Exception
            
    def changLiveChannelByChanneldownKey(self,times, playtimes):
        for i in range(times):
            self.a.input.channel_down()
            time.sleep(playtimes)
            if not self.isPlaying():
                raise Exception
            
    def changeChannelUpToDown(self, times, playtime):
          self.a.input.center()
          time.sleep(5)
          for i in range(times):
              self.a.input.up()
              time.sleep(1)
              if not self.isPlaying():
                  raise Exception
      '''    

if __name__ == '__main__':
    unittest.main()


