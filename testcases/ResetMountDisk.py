# -*- coding: utf-8 -*-
'''
Created on 2013-5-24

@author: Administrator
'''
import unittest
import Stability
import re, time, os

class TestReset(unittest.TestCase):


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
    
    def connectDevice(self):
        os.system('adb disconnect %s' %self.id)
        time.sleep(5)
        os.system('adb connect %s' %self.id)
        os.system('adb -s %s root' %self.id)
        time.sleep(2)
        os.system('adb connect %s' %self.id)
    
    def launchSettings(self):
        s=self.a.ui.screen()
        for i in range(1,7):
            if 'searchDesktop' in s.ids(): 
                break;
            else:
                self.a.input.home()
                time.sleep(5)
                s.refresh()
        self.a.input.right(2)
        time.sleep(5)
        self.a.input.down(5)
        time.sleep(2)
        for i in range(5):
                if 'application_desktop' in self.a.ui.screen().ids():
                    self.a.input.down(3)
                    break
                else:
                    self.a.input.right()
                    time.sleep(2)
        if i == 4:
            self.error = 'cannot move cursor to settings'
            return False
        self.a.input.right(4)
        self.a.input.center()
        time.sleep(2)
        return True
    
    def getCurrentVolume(self):
        try:
            cmd = "dumpsys media.audio_policy|busybox awk -F ' ' '/03/{print $7}'|busybox cut -d ',' -f 1|busybox tail -1"
            currentVolume = self.a.device.sh(cmd).encode("utf-8").strip()
            print currentVolume
            return currentVolume
        except Exception, e:
            self.error = "meet exception while get the volume"
            raise Exception
            
    def launchLetv(self):
        try:
            for i in range (6):
                s = self.a.ui.screen()
                print "finding live tv"
                time.sleep(5)
                if len(s.ids()) < 11 and "livetv_desktop" in str(s.ids()):
                    return True
                    break
                else:
                    self.a.input.home()
            self.error = "failed to launch live tv"
            return False
        except:
            self.error += "meet exception while finding live TV"
            return False

    def testReset(self):
        '''恢复出厂设置判断外界存储是否识别|操作步骤：;1. 恢复出厂设置；'''
        try:
            self.a.device.sh('input keyevent 176')
            self.a.input.left(8)
            self.a.input.right(4)
            time.sleep(2)
            self.a.input.right()
            self.a.input.center()
            self.a.input.down(20)
            w=self.a.ui.screen()
            if "reset" in w.ids():
                self.a.input.center()
                self.a.input.down(3)
                self.a.input.center()
                print "wait for 280s"
                #here while coast more time if this is first time to reset system
                time.sleep(280)
                self.connectDevice()
                time.sleep(2)
                self.a.input.back()
                time.sleep(2)
                self.a.input.left()
                self.a.input.center()
                time.sleep(10)
            mntl = self.a.device.sh("df | grep /mnt/usb/sda1")
            if "/mnt/usb/sda1" not in mntl:
                print "cannot mount /mnt/usb/sda1"
                self.error = 'cannot mount /mnt/usb/sda1'
                raise Exception	
        except Exception, e:
            self.a.log.debug("", "\n testReset")
            self.fail("Error happened: %s %s" % ( self.error, e))  
            
    def _testVolumeReset(self):
        '''恢复出厂设置音量是否恢复到默认值|恢复出厂设置后检查音量是否恢复到默认值'''
        try:
            self.a.device.sh('input keyevent 24')
            time.sleep(1)
            self.a.device.sh('input keyevent 24')
            time.sleep(1)
            self.a.device.sh('input keyevent 24')
            time.sleep(1)
            self.a.device.sh('input keyevent 24')
            time.sleep(1)
            self.a.device.sh('input keyevent 24')
            time.sleep(1)
            self.a.device.sh('input keyevent 24')
            time.sleep(1)
            startVolume = self.getCurrentVolume()
            print 'start: %s' %startVolume
            self.a.device.sh('input keyevent 176')
            self.a.input.right(10)
            self.a.input.left()
            self.a.input.center()
            self.a.input.down(20)
            w=self.a.ui.screen()
            if "reset" in w.ids():
                self.a.input.center()
                self.a.input.down(3)
                self.a.input.center()
                print "wait for 100s"
                #here while coast more time if this is first time to reset system
                time.sleep(200)
                self.connectDevice()
                self.a.input.back(3)
                
            if not self.launchLetv():
                raise Exception
            endVolume = self.getCurrentVolume()
            print 'end: %s' %endVolume
            if endVolume == startVolume or endVolume != '10':
                self.error = "the volume is not the default value"
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testVolumeReset")
            self.fail("Error happened: %s %s" % ( self.error, e)) 
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
