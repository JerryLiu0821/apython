# -*- coding: utf-8 -*-
import android, unittest, time, sys, traceback
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

    def testNormal(self):
        """升级到正常版本 | U盘升级"""
        try :
            #self.a.device.sh("rm /mnt/usb/sda1/update.zip")
            #self.a.device.sh("cp /mnt/usb/sda1/update_normal.zip /mnt/usb/sda1/update.zip")
            self.USBUpgrade()
            today = datetime.date.today().strftime('%Y-%m-%d')
            self.checkRelease('2014-09-04')
            #self.checkRelease(today)
            self.a.input.back()
            time.sleep(2)
            self.a.input.left()
            self.a.input.center()
        except Exception, e :
            self.a.log.debug("", "\n testNormal")
            self.fail(self.error)
    def testDRM(self):
        """升级到DRM版本 | U盘升级"""
        try :
            self.a.device.sh("rm /mnt/usb/sda1/update.zip")
            self.a.device.sh("cp /mnt/usb/sda1/update_drm.zip /mnt/usb/sda1/update.zip")
            self.USBUpgrade()
            today = datetime.date.today().strftime('%Y-%m-%d')
            self.checkRelease('2014-07-01')
            #self.checkRelease(today)
            self.a.input.back()
            time.sleep(2)
            self.a.input.left()
            self.a.input.center()
        except Exception, e :
            self.a.log.debug("", "\n testDRM")
            self.fail(self.error)
            
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
    def _testSTAB_USB_UPGRADE_TO_OLD(self):
        """升级到旧版本 | U盘升级"""
        try :
            self.USBUpgrade()
            self.checkRelease('2014-06-18')
        except Exception, e :
            self.a.log.debug("", "\n testSTAB_USB_UPGRADE_TO_OLD")
            self.fail(self.error)
    
    def testSTAB_USB_UPGRADE_Online(self):
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
            
    def _testOnlineUpgradeTime(self):
        '''在线升级最新版本用时|在线升级最新版本用时测试'''
        try:
            self.a.device.sh("rm /mnt/usb/sda1/update.zip")
            self.a.device.sh("cp /mnt/usb/sda1/update_old.zip /mnt/usb/sda1/update.zip")
            self.USBUpgrade()
            self.connect()
            if not self.OnlineUpgrade():
                raise Exception
            self.a.input.center()
            startTime = time.time()
            print "upgrading start time is %s" %startTime
            os.system ('adb disconnect %s' %self.id)
            time.sleep(20)
            flag = True
            while flag:
                print 'check connection'
                os.system("adb disconnect %s" %self.id)
                result = os.popen("adb connect %s" %self.id).readline()
                if 'unable' not in result and 'no such' not in result:
                    os.system("adb -s %s root" %self.id)
                    os.system("adb connect %s" %self.id)
                    flag = False
            endTime = time.time()
            print "end time is %s" %endTime
            upgradeTime = endTime - startTime
            print upgradeTime
            if upgradeTime > 300:
                self.error = "upgrade time is more than 5 minutes"
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testOnlineUpgradeTime")
            self.fail(self.error)
    
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
            
    def _testUserDataAfterOnlineUpgrade(self):
        '''在线升级后系统设置数据不会被清除|在线升级后，系统设置数据不会被清除'''
        try:
            '''check user data before update'''
            self.a.device.sh("rm /mnt/usb/sda1/update.zip")
            self.a.device.sh("cp /mnt/usb/sda1/update_old.zip /mnt/usb/sda1/update.zip")
            self.USBUpgrade()
            self.connect()
            self.a.device.sh("input keyevent 176")
            self.a.input.down()
            self.a.input.right(4)
            self.a.input.left()
            self.a.input.center()
            self.a.input.down(3)
            self.a.input.center()
            userData1 = "关闭".decode("utf-8")
            if userData1 not in self.a.ui.screen().texts()[5]:
                userData1 = "开启".decode("utf-8")
            print userData1
            self.a.input.down(2)
            self.a.input.center()
            userData2 = "12小时制".decode("utf-8")
            if userData2 not in self.a.ui.screen().texts()[6]:
                userData2 = "24小时制".decode("utf-8")
            print userData2
            self.a.input.back(2)
            self.OnlineUpgrade()
            self.a.input.center()
            print "Upgrading"
            time.sleep(self.upgradeTime)
            self.connect()
            time.sleep(5)
            self.a.device.sh("input keyevent 176")
            self.a.input.down()
            self.a.input.right(4)
            self.a.input.left()
            self.a.input.center()
            self.a.input.down(3)
            print self.a.ui.screen().texts()[5]
            if userData1 not in self.a.ui.screen().texts()[5]:
                self.error = 'user data 1 is changed after upgrading'
                raise Exception
            self.a.input.down(2)
            print self.a.ui.screen().texts()[6]
            if userData2 not in self.a.ui.screen().texts()[6]:
                self.error = 'user data 2 is changed after upgrading'
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testUserDataAfterOnlineUpgrade")
            self.fail(self.error)
            
    def _testCheckVolumeDataAfterOTA(self):
        '''在线升级后声音数据不会被清除|在线升级后，声音数据不会被清除'''
        try:
            self.a.device.sh("rm /mnt/usb/sda1/update.zip")
            self.a.device.sh("cp /mnt/usb/sda1/update_old.zip /mnt/usb/sda1/update.zip")
            self.USBUpgrade()
            self.connect()
            if not self.launchLetv():
                raise Exception
            self.a.input.volume_up(5)
            startVolume = self.getCurrentVolume()
            self.a.input.back(2)
            if not self.OnlineUpgrade():
                raise Exception
            self.a.input.center()
            print "Upgrading"
            time.sleep(self.upgradeTime)
            self.connect()
            time.sleep(5)
            if not self.launchLetv():
                raise Exception
            endVolume = self.getCurrentVolume()
            if startVolume != endVolume:
                self.error = "volume in live TV screen is changed"
                raise Exception        
        except Exception, e:
            self.a.log.debug("", "\n testCheckVolumeDataAfterOTA")
            self.fail(self.error)
            
    def _testCheckLogAfterOTA(self):
        '''在线升级后升级log可以被保存|在线升级后，升级log会被成功保存'''
        try:
            self.a.device.sh("rm /mnt/usb/sda1/update.zip")
            self.a.device.sh("cp /mnt/usb/sda1/update_old.zip /mnt/usb/sda1/update.zip")
            self.USBUpgrade()
            self.connect()
            cmd = "ls -l /cache/recovery/ | busybox awk -F ' ' '{print $6}'"
            os.system("adb -s %s root" %self.id)
            os.system("adb connect %s" %self.id)
            oldLogTime = self.a.device.sh(cmd)
            print oldLogTime
            if not self.OnlineUpgrade():
                raise Exception
            self.a.input.center()
            print "Upgrading"
            time.sleep(self.upgradeTime)
            self.connect()
            time.sleep(5)
            if not self.launchLetv():
                raise Exception
            newLogTime = self.a.device.sh(cmd)
            print newLogTime
            if oldLogTime == newLogTime:
                self.error = "failed to save the log"
                raise Exception        
        except Exception, e:
            self.a.log.debug("", "\n testCheckLogAfterOTA")
            self.fail(self.error)
            
    def _testOTAWithouPackage(self):
        '''无在线升级包的情况下在线升级系统|在线升级，但是没有在线升级包'''
        try:
            self.stabdl.open_intent('OnlineUpgrade')
            time.sleep(5)
            self.a.input.down(3)
            self.a.input.up(2)
            self.a.input.center()
            time.sleep(2)
            w = self.a.ui.waitfor(anyof=[
                self.a.ui.widgetspec(id='prompttext'),
                self.a.ui.widgetspec(id='onlineupdateinfoButton'),
                self.a.ui.widgetspec(id='filetext'),
                              ]).id()
            if w == 'prompttext':
                message = self.a.ui.waitfor(id='prompttext').text().encode('utf-8')
                print message
                if message != "系统版本已经是最新":
                    self.error = "the error message is not expected"
                    raise Exception
            else:
                self.error = 'failed to display the correct message'
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testOTAWithouPackage")
            self.fail(self.error)
            
    def _testStableUpgradeVersion(self):
        '''升级到stable版最新版本 | U盘升级'''
        try :
            oldVersion = self.a.device.sh('getprop | grep ro.letv.release.version')
            print oldVersion
            self.USBUpgrade()
            self.connect()
            newVersion = self.a.device.sh('getprop | grep ro.letv.release.version')
            print newVersion
            if oldVersion == newVersion:
                self.error = "after upgrade, the version is not the latest."
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testStableUpgradeVersion")
            self.fail(self.error)
            
    def _testUpgradeAfterDownload(self):
        '''usb升级下载完成后不重启，退出当前界面再进入升级'''
        try:
            self.a.device.sh("rm /mnt/usb/sda1/update.zip")
            self.a.device.sh("cp /mnt/usb/sda1/update_new.zip /mnt/usb/sda1/update.zip")
            self.stabdl.open_intent('OnlineUpgrade')
            self.a.input.down(3)
            self.a.input.up()
            self.a.input.center()
            w = self.a.ui.waitfor(anyof=[
                    self.a.ui.widgetspec(id='prompttext'),
                    self.a.ui.widgetspec(id='ok_usb_buttion'),
                    self.a.ui.widgetspec(id='filetext'),
                                  ]).id()
            if w == 'prompttext':
                self.error = 'failed to upgrade, pls check the network or if there is newer version.'
                self.a.input.center()
                self.error = 'Can not find new release on USB device.'
                raise Exception
            else:
                self.a.input.down()
                self.a.input.center()
            print "Downloading"
            time.sleep(self.downloadTime)
            self.a.input.back()
            time.sleep(5)
            self.stabdl.open_intent('OnlineUpgrade')
            self.a.input.down(3)
            self.a.input.up()
            self.a.input.center()
            print "Upgrading"
            time.sleep(self.upgradeTime)
            today = datetime.date.today().strftime('%Y-%m-%d')
            self.checkRelease(today)
        except Exception, e:
            self.a.log.debug("", "\n testUpgradeAfterDownload")
            self.fail(self.error)
            
    def _testCancelDownload(self):
        '''usb升级下载时，取消下载升级包：1. 进入离线升级，复制下载升级包 2. 下载过程中取消下载 Fail项：1.无法停止下载 2.无法返回到下载时的前一界面'''
        try:
            self.a.device.sh("rm /mnt/usb/sda1/update.zip")
            self.a.device.sh("cp /mnt/usb/sda1/update_new.zip /mnt/usb/sda1/update.zip")
            self.stabdl.open_intent('OnlineUpgrade')
            self.a.input.down(3)
            self.a.input.up()
            self.a.input.center()
            w = self.a.ui.waitfor(anyof=[
                    self.a.ui.widgetspec(id='prompttext'),
                    self.a.ui.widgetspec(id='ok_usb_buttion'),
                    self.a.ui.widgetspec(id='filetext'),
                                  ]).id()
            if w == 'prompttext':
                self.error = 'failed to upgrade, pls check the network or if there is newer version.'
                self.a.input.center()
                self.error = 'Can not find new release on USB device.'
                raise Exception
            else:
                self.a.input.down()
                self.a.input.center()
                time.sleep(5)
                print "Downloading and then cancelling the downloading"
                self.a.input.center()
                time.sleep(5)
                if 'updateFileProgressBar' in self.a.ui.screen().ids():
                    self.error = "failed to cancel the downloading progress"
                    raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testCancelDownload")
            self.fail(self.error)
            
    def _testUpgradeWithoutExternalStorage(self):
        '''USB升级但未接入外接设备'''
        try:
            os.system ('adb -s %s root'%self.id)
            time.sleep(2)
            os.system ('adb connect '+ self.id )
            cmd1 = "mount | busybox awk -F ' ' '/\/mnt\/usb\/sd[aA-zZ][1-9]/{print $1}'"
            cmd2 = "mount | busybox awk -F ' ' '/\/mnt\/usb\/sd[aA-zZ][1-9]/{print $2}'"
            cmd3 = "mount | busybox awk -F ' ' '/\/mnt\/usb\/sd[aA-zZ][1-9]/{print $3}'"
            deviceList = self.a.device.sh(cmd1).encode("utf-8").strip().split('\r\n')
            mountPoint = self.a.device.sh(cmd2).encode("utf-8").strip().split('\r\n')
            type = self.a.device.sh(cmd3).encode("utf-8").strip().split('\r\n')
            
            for i in range(0, len(deviceList)):
                self.a.device.sh("umount %s" %mountPoint[i])
            
            self.stabdl.open_intent('OnlineUpgrade')
            self.a.input.down(3)
            self.a.input.up()
            self.a.input.center()
            s = '未检测到系统更新文件'
            message = self.a.ui.screen().texts()
            print message[0]
            for i in range(0, len(deviceList)):
                if type[i] == 'fuseblk':
                    type[i] = 'ntfs'
                print "mount -t %s -rw %s %s" %(type[i], deviceList[i], mountPoint[i])
                result = self.a.device.sh("mount -t %s -rw %s %s" %(type[i], deviceList[i], mountPoint[i]))
                if result != '':
                    self.error = result
                    raise Exception
                time.sleep(3)
                
            if s.decode('utf-8') not in message[0]:
                self.error = "failed to give the correct prompt"
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testUpgradeWithoutExternalStorage")
            self.fail(self.error)
    
    def _testUpgradeWithoutPackage(self):
        '''USB升级但未拷入升级包'''
        try:
            '''
            cmd = "df | awk -F ' ' '/\/mnt\/usb\/sd[a-z][0-9]/{print $1}'"
            storagePath = self.a.device.sh(cmd).encode("utf-8").strip().split('\r\n')
            for i in range(len(storagePath)):
                cmd1 = "mv %s/update.zip %s/update_new.zip" %(storagePath[i], storagePath[i])
                self.a.device.sh(cmd1)
            '''
            self.a.device.sh("rm /mnt/usb/sda1/update.zip")
            self.stabdl.open_intent('OnlineUpgrade')
            self.a.input.down(3)
            self.a.input.up()
            self.a.input.center()
            s = '未检测到系统更新文件'
            message = self.a.ui.screen().texts()
            print message[0]
            '''
            for i in range(len(storagePath)):
                cmd2 = "mv %s/update_new.zip %s/update.zip" %(storagePath[i], storagePath[i])      
                self.a.device.sh(cmd2)
            '''
            if s.decode('utf-8') not in message[0]:
                self.error = "failed to give the correct prompt"
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testUpgradeWithoutPackage")
            self.fail(self.error)
                
            
if __name__ == '__main__':
    unittest.main()



