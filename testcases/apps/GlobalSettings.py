# -*- coding: utf-8 -*-
'''
Created on Mar 27, 2013

@author: liujian
'''
import unittest
import re, time, commands,sys
sys.path.append('../testcases')
import Stability


class TestGlobalSettings(unittest.TestCase):

    def setUp(self):
        try :
            self.error = ''
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.id = self.setup.device_id
            self.stabdl = Stability.StabDL(self.a)
            self.a.input.back(3)

        except Exception, e :
            self.a.log.debug("", "\n Set up")


    def tearDown(self):
        self.a.input.back(3)
    
    def test3D(self):
        """打开关闭3D|在设置中打开关闭3D"""
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.settings.TestSettings#test3D"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n test3D")
            self.fail("Error happened: %s %s" % ( self.error, e))

    def _test3D(self):
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
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.settings.TestSettings#testMiracast"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testMiracast")
            self.fail("Error happened: %s %s" % ( self.error, e))
            
    def _testMiracast(self):
        """Miracast打开关闭|在设置中打开关闭Miracast"""
        try:
            self.a.device.sh('input keyevent 176')
            self.a.input.left(8)
            self.a.input.down()
            self.a.input.right(3)
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

    def _testInstallApks(self):
        """安装外部应用|安装多个外部应用"""
        try:
            apksp = '../testcases/setup/apks/'
            apks = commands.getoutput("ls %s" %apksp).split('\n')
            for apk in apks:
                os.system("adb -s %s install %s/%s" %(self.id, apksp, apk))
            
            
        except Exception, e :
            self.a.log.debug("", "\n testInstallApks")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    
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
