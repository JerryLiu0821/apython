# -*- coding: utf-8 -*-
import android, unittest, time, sys, traceback
sys.path.append('../testcases')
import Stability
from random import choice
import datetime
import runtests
import os



class testUpgrade(unittest.TestCase):

    def setUp(self):
        try :

            self.error = ''
            self.downloadTime = 80
            self.upgradeTime = 350
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.stabdl = Stability.StabDL(self.a)
            self.id = self.setup.device_id   
            self.a.input.back(3)
        except :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        self.a.input.back(3) 
    
    def USBUpgrade(self):
        self.stabdl.open_intent('OnlineUpgrade')
        self.a.input.down(4)
        time.sleep(2)
        self.a.input.up()
        times=1
        while str(self.a.ui.waitfor(isFocused=True).id()) != 'usb' and times <5:
            self.a.input.up()
            time.sleep(2)
            times +=1
        if times ==5:
            self.error = "cannot find usb upgrade"
            raise Exception
        time.sleep(1)
        self.a.input.center()
        time.sleep(1)
        w = self.a.ui.screen()
        if 'filetext' not in w.ids():
            self.error = 'cannot enter system update page'
            raise Exception
        self.a.input.down()
        self.a.input.center()
        print "Downloading"
        time.sleep(self.downloadTime)
        self.a.input.center()
        print "Upgrading"
        time.sleep(self.upgradeTime)
    
    def OnlineUpgrade(self):
        self.stabdl.open_intent('OnlineUpgrade')
        time.sleep(5)
        self.a.input.down(3)
        self.a.input.up(2)
        self.a.input.center()
        time.sleep(2)
        self.a.input.down(3)
        self.a.input.center()
        time.sleep(2)
        timeout = 0
        while '重启更新'.decode('utf-8') not in self.a.ui.screen().texts()[9]:
            print self.a.ui.screen().texts()[4]
            time.sleep(5)
            timeout += 5
            print timeout
            if timeout >= 300:
                self.error = 'download build timeout'
                return False
        return True
        

    def waitforId(self,idname):
        result = ''
        try:
            result = self.a.ui.waitfor(id=idname).text()
        except:
            pass
        return str(result)
    
    def connect(self):
        print 'connect'
        os.system ('adb disconnect ' + self.id)
        for i in range(1, 6):
            result = os.popen('adb connect ' + self.id[:-5]).readlines()
            if 'unable'  not in str(result):
                break
            time.sleep(30)
            
        os.system ('adb -s %s root' % self.id)
        time.sleep(5)
        os.system ('adb connect ' + self.id)
        self.a.input.back(3)
        time.sleep(10)
        
    def checkRelease(self, date):
        self.connect()
        print "Checking release..."        
        version = self.a.device.sh('getprop | grep ro.letv.release.date')
        print version
        if date == '':
            cmd = os.popen ('date \"+%m%d\"')
            date = cmd.readline().strip()
        if date not in version:
            self.error = 'after upgrade, the version is not the latest.'
            raise Exception   

    def testSTAB_USB_UPGRADE_TO_NEW(self):
        """U盘升级 | U盘升级"""
        try :
            #self.a.device.sh("rm /mnt/usb/sda1/update.zip")
            #self.a.device.sh("cp /mnt/usb/sda1/update_new.zip /mnt/usb/sda1/update.zip")
            self.USBUpgrade()
            today = datetime.date.today().strftime('%Y-%m-%d')
            #self.checkRelease('2014-07-24')
            self.checkRelease(today)
            self.a.input.back()
            time.sleep(2)
            self.a.input.left()
            self.a.input.center()
        except Exception, e :
            self.a.log.debug("", "\n testSTAB_USB_UPGRADE_TO_NEW")
            self.fail(self.error)
    
    def _testSTAB_USB_UPGRADE_Online(self):
        """在线升级到最新版本 | 在线升级"""
        try:
            #self.a.device.sh("rm /mnt/usb/sda1/update.zip")
            #self.a.device.sh("cp /mnt/usb/sda1/update_old.zip /mnt/usb/sda1/update.zip")
            #self.USBUpgrade()
            #self.connect()
            if not self.OnlineUpgrade():
                raise Exception
            self.a.input.center()
            print "Upgrading"
            
            time.sleep(self.upgradeTime)
            today = datetime.date.today().strftime('%Y-%m-%d')
            self.checkRelease(today)
        except Exception, e:
            self.a.log.debug("", "\n testSTAB_USB_UPGRADE_Online")
            self.fail(self.error)

if __name__ == '__main__':
    unittest.main()



