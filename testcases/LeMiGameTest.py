# -*- coding: utf-8 -*-
'''
Created on Aug 4, 2014

@author: ZhaoJianning
'''
import unittest
import Stability
import time, re, commands
import sys,os, subprocess
import threading
reload(sys)
sys.setdefaultencoding('utf8')

class TestLeMiGame(unittest.TestCase):


    def setUp(self):
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.id = self.setup.device_id
        self.filePath = "../testcases/setup"
        self.package = "com.lemi.controller.lemigameassistance"
        self.apk = "LemiGameAssistance_v_1.0.1.21_release.apk"
        self.error = ''
        self.a.input.back(3)


    def tearDown(self):
        pass

    def testInstallSingleGame(self):
        """乐米游戏，安装下载乐米游戏的单个游戏|点击一个游戏下载安装"""
        self.jar = "LeMiAutoTest.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.lemi.LeMiGame#testInstallSingleGame"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testInstallSingleGame")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testInstallManyGame(self):
        """乐米游戏，安装下载多个乐米游戏|进入分类，点击推荐首页的所有游戏下载安装"""
        self.jar = "LeMiAutoTest.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.lemi.LeMiGame#testInstallManyGame"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testInstallManyGame")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testStartFromGame(self):
        """乐米游戏下载安装完成后启动游戏|下载安装完成后直接启动游戏"""
        self.jar = "LeMiAutoTest.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.lemi.LeMiGame#testStartFromGame"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testStartFromGame")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testStartFromMyGameList(self):
        """乐米游戏，从我的游戏列表里启动所有下载的乐米游戏|从我的游戏里启动所有下载的乐米游戏"""
        self.jar = "LeMiAutoTest.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.lemi.LeMiGame#testStartFromMyGameList"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testStartFromMyGameList")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testStartFromDesktop(self):
        """乐米游戏，从应用桌面启动多个乐米游戏|从应用桌面启动多个乐米游戏"""
        self.jar = "LeMiAutoTest.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.lemi.LeMiGame#testStartFromDesktop"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testStartFromDesktop")
            self.fail("Error happened: %s %s" % (self.error, e))
          
    def testEnterExitLemi(self):
        """乐米游戏，关闭再启动乐米游戏|1.清除应用数据，2.启动乐米游戏，3.在乐米游戏移动光标，4.退出乐米游戏"""
        self.jar = "LeMiAutoTest.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.lemi.LeMiGame#testEnterExitLemi"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testEnterExitLemi")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testUninstall(self):
        """乐米游戏，卸载全部应用|卸载全部乐米游戏应用"""
        self.jar = "LeMiAutoTest.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.lemi.LeMiGame#testUninstall"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testUninstall")
            self.fail("Error happened: %s %s" % (self.error, e))

    def installOlderApk(self):
        resultUninstall = os.popen("adb -s %s uninstall %s" %(self.id, self.package)).read()
        print resultUninstall
        if 'Success' not in resultUninstall:
            self.error = "uninstall the current version failed"
            raise Exception
        resultInstall = os.popen("adb -s %s install %s/%s" %(self.id, self.filePath, self.apk)).read()
        if 'Success' not in resultInstall:
             self.error = "install the older version failed"
             raise Exception
        
    def testUpgrade(self):
        """乐米游戏升级测试|乐米游戏升级测试"""
        #uninstall the current version
        self.installOlderApk()
         
        self.jar = "LeMiAutoTest.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.lemi.LeMiGame#testUpgrade"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testUpgrade")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def rebootDevice(self):
        self.a.device.sh('su -c reboot reboot')
        
    def connect(self):
        for i in range(1, 15):
            print '%s connect' %i
            os.system ('adb disconnect ' + self.id)
            time.sleep(1)
            os.system('adb connect ' + self.id)
            time.sleep(1)
            getprop = subprocess.Popen('adb -s %s shell getprop | grep version' %self.id, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            print getprop 
            if 'device not found' not in str(getprop):
                print 'connected to device ' + self.id
                os.system("adb -s %s root" %self.id)
                time.sleep(3)
                os.system('adb connect ' + self.id)
                return True
            time.sleep(10)
        return False
    
    def testRebootWhileUpgrade(self):
        """乐米游戏，升级乐米apk过程中重启电视|升级乐米过程中重启电视"""
        #uninstall the current version
        self.installOlderApk()
         
        self.jar = "LeMiAutoTest.jar"
        #self.jar = "UiAutomator.jar"
        self.case1 = "com.letv.lemi.RebootWhileUpgrade#testRebootWhileUpgrade"
        self.case2 = "com.letv.lemi.LeMiGame#testOpenApk"
        try:
            ua1 = Stability.UiAutomator(self.id, self.jar, self.case1)
            result1, info1 = ua1.runtest()
            if result1 != 'PASS':
                self.error = str(info1)
                raise Exception
            self.rebootDevice()
            time.sleep(180)
            if not self.connect():
                self.error = 'failed to reboot device'
                raise Exception
            ua2 = Stability.UiAutomator(self.id, self.jar, self.case2)
            result2, info2 = ua2.runtest()
            if result2 != 'PASS':
                self.error = str(info2)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testUpgrade")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testCancleUpgrade(self):
        """乐米游戏，取消升级测试|取消升级测试"""
        #uninstall the current version
        self.installOlderApk()
         
        self.jar = "LeMiAutoTest.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.lemi.LeMiGame#testCancleUpgrade"
        try:
            
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testUpgrade")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testMoveInCategory(self):
        '''乐米游戏，在分类栏里上下移动|进入分类页里上下移动焦点'''
        self.jar = "LeMiAutoTest.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.lemi.LeMiGame#testMoveInCategory"
        try:
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            
        except Exception, e :
            self.a.log.debug("", "\n testMoveInCategory")
            self.fail("Error happened: %s %s" % (self.error, e))
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
