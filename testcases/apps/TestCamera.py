# -*- coding: utf-8 -*-
'''
Created on 2014-03-25

@author: ZhaoJianning
Modified by WangHairui on 2014-09-12
'''

import unittest
import os,sys
sys.path.append('../testcases')
import Stability
import time
import runtests
import re
import android
import datetime

class TestCamera(unittest.TestCase):
    
    def setUp(self):
        self.error = ''
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.id = self.setup.device_id
        self.stabdl = Stability.StabDL(self.a) 
        self.path = "/mnt/sdcard/LepiPhoto"
        self.a.input.back(3)
        
    def tearDown(self):
        self.a.input.back(3)
        
    def launchCamera(self):
        try:
            act = "android.intent.action.MAIN"
            cat = "android.intent.category.LAUNCHER"
            flg = "0x10200000"
            cmp = "com.letv.camera/.CameraActivity"
            cmd = "am start -a %s -c %s -f %s -n %s" %(act, cat, flg, cmp)
            
            #self.a.device.sh("su")
            result = self.a.device.sh(cmd)
            print result
            if "Exception" in str(result) or "Error" in str(result):
                return False
            return True
        except:
            self.error += "launch camera meets exception"
            return False
        
    def checkPhoto(self, spath):
        photoList = self.a.device.sh("ls %s" %spath)
        print photoList
        today = datetime.date.today().strftime('%Y%m%d')
        if today in str(photoList):
            return True
        return False

    def pullPhoto(self):
        workd = os.path.join(android.log.report_directory(), android.log.logs_directory())
        os.system('adb -s %s pull %s %s' %(self.id,self.path,workd))
        self.a.device.sh("rm -rf %s/*.jpg" %self.path)
    '''    
    def testCamera(self):
        """测试摄像头驱动工作正常|操作步骤：1. 命令行启动摄像头 2. 拍下照片 Fail项：1. 启动摄像头失败 2. 照片未拍下"""
        try:
            print "test camera"
            self.a.device.sh("rm %s/*" %self.path)
            if not self.launchCamera():
                self.error += "launch camera failed"
                raise Exception
            time.sleep(10)
            self.a.input.center()
            time.sleep(10)
            if not self.checkPhoto():
                self.error = "failed to capture the photo"
                raise Exception
            self.pullPhoto()
        except Exception, e:
            self.a.log.debug("", "\n test camera")
            self.fail("Error happened: %s %s" %(self.error, e))
    '''
        
    def testCamera(self):
        """测试拍照工作正常|操作步骤：1. 命令行启动摄像头 2. 拍下照片 Fail项：1. 启动摄像头失败 2. 照片未拍下"""
    
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.camera.Camera#testCapture"
        try:
            self.a.device.sh("rm -rf %s/*" %self.path)
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            if not self.checkPhoto(self.path):
                self.error = "failed to capture the photo"
                raise Exception
            self.pullPhoto()
        except Exception, e :
            self.a.log.debug("", "\n testCamera")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testOpenExit(self):
        """测试打开退出乐拍app|操作步骤：1. 打开乐拍应用 2. 退出乐拍应用 Fail项：1. 无法打开或退出乐拍 2.系统crash"""
    
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.camera.Camera#testOpenExit"
        try:
            self.a.device.sh("rm -rf %s/*" %self.path)
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testCamera")
            self.fail("Error happened: %s %s" % (self.error, e))
         
    def testVideo(self):
        """测试摄像头视频拍摄工作正常|操作步骤：1. 命令行启动摄像头 2. 摄像 Fail项：1. 启动摄像头失败 2. 视频未拍下"""
    
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.camera.Camera#testVideo"
        videoPath = "/mnt/usb/sda1/LepiVideo"
        try:
            self.a.device.sh("rm -rf %s/*" %videoPath)
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
            if not self.checkPhoto(videoPath):
                self.error = "failed to capture the video"
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testCamera")
            self.fail("Error happened: %s %s" % (self.error, e))   
            
    def testSwitch(self):
        """测试摄像拍照模式来回切换|操作步骤：1. 在拍照和摄像两个模式来回切换"""
    
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.camera.Camera#testSwitch"
        try:
            #self.a.device.sh("rm -rf %s/*" %self.path)
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testCamera")
            self.fail("Error happened: %s %s" % (self.error, e))  
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testBrowser']
    unittest.main()
            
            
        

