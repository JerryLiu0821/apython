# -*- coding: utf-8 -*-
'''
Created on Jan 15, 2014

@author: liujian
'''
import unittest
import serial, time
import android

class TestSerial(unittest.TestCase):


    def setUp(self):
        self.error = ''
        self.ser = ''
        try:
            self.ser = serial.Serial(port='/dev/ttyUSB2', baudrate=115200, timeout=0)
            if  not self.ser.isOpen():
                self.error = 'cannot open %s' % self.ser.port
                raise Exception
        except Exception:
            self.a.log.debug("", "\n setUp")
            self.fail("Error happened: %s" % self.error)
        

    def tearDown(self):
        if self.ser.isOpen():
            self.ser.close()
    
    
    def sendCommand(self, command):
        self.ser.write(command+'\n')

    def testNetWorkConnectTime(self):
        """重启联网时间|重启，判断网络是否链接"""
        try:
            self.sendCommand('su -c reboot reboot')
            start = time.time()
            time.sleep(10)
            self.sendCommand('su')
            self.ser.readlines()
            self.sendCommand('netcfg')
            time.sleep(1)
            lines = self.ser.readlines()
            print lines
            while '192.168.1.1' not in str(lines):
                self.sendCommand('netcfg')
                time.sleep(1)
                lines = self.ser.readlines()
                print lines
            end = time.time()
            during = end - start
            print during
            android.log.debug("", "raise self.failureException('联网时间为: %s s')" %during)
        except Exception:
            self.fail("Error happened: %s" % self.error)
        
    def testSystemStartTime(self):
        """开机系统启动时间| reboot到系统起来的时间"""
        try:
            self.sendCommand('su -c reboot reboot')
            start = time.time()
            time.sleep(20)
            self.sendCommand('su')
            time.sleep(1)
            self.ser.readlines()
            time.sleep(0.5)
            self.sendCommand('ps | grep /system/bin/bootanimation')
            time.sleep(1)
            lines = self.ser.readlines()
            #size = self.ser.inWaiting()
            #lines = self.ser.read(size)
            lines = lines[1:]
            print lines
            while 'bootanimation' in str(lines):
                self.sendCommand('ps | grep /system/bin/bootanimation')
                time.sleep(1)
                #size = self.ser.inWaiting()
                #lines = self.ser.read(size)
                lines = self.ser.readlines()
                lines = lines[1:]
                print lines
            end = time.time()
            during = end - start
            print during
            android.log.debug("", "raise self.failureException('loading time: %s s')" %during)
        except Exception:
            self.fail("Error happened: %s" % self.error)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
