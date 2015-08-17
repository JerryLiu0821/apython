# -*- coding: utf-8 -*-
'''
Created on Mar 27, 2013

@author: liujian
'''
import unittest
import Stability,android
import re, time, commands, os


class TestGlobalSettings(unittest.TestCase):

    def setUp(self):
        try :
            self.error = ''
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.stabdl = Stability.StabDL(self.a)
            self.id = self.setup.device_id
            self.a.input.back(3)

        except Exception, e :
            self.a.log.debug("", "\n Set up")


    def tearDown(self):
        self.a.input.back(3)
    

    def test3D(self):
        """打开关闭3D|在设置中打开关闭3D"""
        try:
            #self.launchLetv()
            self.a.input.home()
            time.sleep(3)
            self.a.input.home()
            time.sleep(3)
            self.a.input.back()
            time.sleep(2)
            self.a.device.sh('input keyevent 176')
            self.a.input.left(8)
            self.a.input.right(2)
            self.a.input.center()
            w = self.a.ui.screen()
            if 'mode_msg' not in str(w.ids()):
                self.error = 'cannot open 3d mode in settings'
                raise Exception
            for i in range(3):
                self.a.input.right()
                self.a.input.center()
                if not self.isOK():
                    raise Exception
            self.a.input.left(3)
            self.a.input.center()
            
        except Exception, e :
            self.a.log.debug("", "\n test3D")
            self.fail("Error happened: %s %s" % ( self.error, e))
            
    def testMiracast(self):
        """Miracast打开关闭|在设置中打开关闭Miracast"""
        try:
            self.a.device.sh('input keyevent 176')
            self.a.input.left(8)
            self.a.input.right(4)
            time.sleep(2)
            self.a.input.center()
            w = self.a.ui.screen()
            if 'miracast_switch' not in str(w.ids()):
                self.error = 'cannot open miracast mode in settings'
                raise Exception
            self.a.input.down()
            
            for i in range(6):
                if '\u5173\u95ed' in str(w.texts()):
                    print 'open miracast'
                    
                else:
                    print 'close miracast'
                self.a.input.center()
                time.sleep(10)    
                if not self.isOK():
                    raise Exception
                w = self.a.ui.screen()
                
            self.a.input.back()
            
        except Exception, e :
            self.a.log.debug("", "\n test3D")
            self.fail("Error happened: %s %s" % ( self.error, e))

    def testInstallApks(self):
        """安装外部应用|安装多个外部应用"""
        try:
            components = ['am start -a android.intent.action.MAIN -n org.xbmc.xbmc/.Splash',
                'am start -a android.intent.action.MAIN  -n org.xbmc.xbmc/.Main',
                'am start -a android.intent.action.MAIN  -n cn.vszone.tv.gamebox/cn.vszone.gamebox.ActivityMain',
                'am start -a android.intent.action.MAIN  -n com.broadin.nanxingbaojian/.LoadActivity',
                'am start -a android.intent.action.MAIN  -n com.tv.clean/.HomeAct',
                'am start -a android.intent.action.MAIN  -n cn.cheerz.ils/cn.cheerz.iptv.MainActivity',
                'am start -a android.intent.action.MAIN  -n com.tencent.mm/.ui.LauncherUI',
                'am start -a android.intent.action.MAIN  -n com.audiocn.kalaok.tv/.activity.MainActivity',
                'am start -a android.intent.action.MAIN  -n com.carrot.iceworld/.CarrotFantasy',
                'am start -a android.intent.action.MAIN  -n cn.kuwo.sing.tv/.view.activity.EntryActivity',
                'am start -a android.intent.action.MAIN  -n com.meishi_tv/.StartActivity',
                'am start -a android.intent.action.MAIN  -n com.moretv.mv/.StartActivity',
                'am start -a android.intent.action.MAIN  -n com.flappybird/org.cocos2dx.cpp.AppActivity',
                'am start -a android.intent.action.MAIN  -n android.videoapp225/android.videoapp.VideoApp',
                'am start -a android.intent.action.MAIN  -n com.broadin.nvxingjiankang/.LoadActivity',
                'am start -a android.intent.action.MAIN  -n com.kugou.playerHD/.activity.SplashActivity',
                'am start -a android.intent.action.MAIN  -n com.example.loseweight/.ShowActivity',
                'am start -a android.intent.action.MAIN  -n com.qiyi.video/.ui.WelcomeActivity',
                'am start -a android.intent.action.MAIN  -n com.netease.vopen.tablet/.activity.WelcomeActivity',
                'am start -a android.intent.action.MAIN  -n com.yodo1tier.ski.tv/com.yodo1.sdk.game.Yodo14GameSplashActivity',
                'am start -a android.intent.action.MAIN  -n android.videoapp195/android.videoapp.VideoApp',
                'am start -a android.intent.action.MAIN  -n com.lovesport.collection/.ShowActivity',
                'am start -a android.intent.action.MAIN  -n com.tmsbg.homeshare.box/.SplashActivity',
                'am start -a android.intent.action.MAIN  -n com.halfbrick.fruitninja/.FruitNinjaActivity',
                'am start -a android.intent.action.MAIN  -n com.trans.runcool/.GameLauncher',
                'am start -a android.intent.action.MAIN  -n com.bf.sgs.hdexp/.MainActivity',
                'am start -a android.intent.action.MAIN  -n com.trans.skee/.GameLauncher']
            path = '../testcases/setup/apks'
            existapps = self.a.device.sh('ls /data/app/')
            apks = commands.getoutput("ls %s/*.apk" %path).split('\n')
            Stability.takeMeminfo(self.id, android.log.report_directory()).meminfo()
            outp = ""
            for a in apks:
                cmd = 'adb -s %s install -r %s' %(self.id, a)
                outp = commands.getoutput(cmd)
                if "Success" not in outp:
                    self.error = outp
                    print outp
            for i in components:
                Stability.takeMeminfo(self.id, android.log.report_directory()).meminfo()
                self.a.device.sh(i)
                time.sleep(5)
                self.a.input.home()
                time.sleep(3)
            
            uninstall = 0
            for i in self.a.device.sh("ls /data/app/").split('\r\n'):
                if i:
                    pkg = i.split('-')[0]
                    cmd = 'pm uninstall %s' %pkg
                    outp = self.a.device.sh(cmd)
                    if 'Success' not in outp:
                        print '%s %s' %(cmd,outp)
                        uninstall += 1
            if uninstall != 0:
                self.error += "uninstall failed"
                raise Exception
                    
        except Exception, e :
            self.a.log.debug("", "\n testInstallApks")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    def gotoAppDesktop(self):
        self.a.device.sh("input keyevent 4401")
        time.sleep(5)
        self.a.input.right(6)
    
    def launchLetv(self):
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
    
    def isOK(self):
        try:
            widgets = self.a.ui.waitfor(
                anyof=[
                    self.a.ui.widgetspec(id='message'),
                    self.a.ui.widgetspec(text='Wait')])
            if widgets == 'message':
                self.a.input.down()
                self.a.input.center()
                self.error = "Force Closed"
                return False
            if widgets == 'Wait':
                self.a.input.down()
                self.a.input.right()
                self.a.input.center()
                self.error = "ANR Happened"
                return False
            """if widgets == idname:
                self.error="Exit Without any prompt message"
                return False"""
            self.a.log.debug("", "No Force Closed & ANR happen!")
            if 'Application Error' in str(self.a.ui.windows()):
                self.a.input.right()
                self.a.input.center()
                return False
            return True
            
        except:
            return True


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
