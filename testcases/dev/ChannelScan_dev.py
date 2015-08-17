# -*- coding: utf-8 -*- 
'''
Created on 2013-3-18

@author: Administrator
'''
import unittest
import android, Stability
import time, re, runtests,os,datetime

class TestChannelScan(unittest.TestCase):

    def setUp(self):
        try:    
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.id = self.setup.device_id
            self.stabdl = Stability.StabDL(self.a)
            self.error = ''
            self.a.input.back(3)

        except Exception, e :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        pass
    
    def _testDTMBAutoScanChannel(self):
        """DTMB自动搜台|进入DTMB并搜台"""
        try:
            self.DTMBAutoScanChannel()
        except Exception, e:
            self.a.log.debug("", "\n testDTMBAutoScanChannel")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    def testATVAutoScanChannel(self):
        """模拟电视自动搜台|进入ATV并搜台"""
        try:
            self.ATVAutoScanChannel()
        except Exception, e:
            self.a.log.debug("", "\n testTVAutoScanChannel")
            self.fail("Error happened: %s %s" % ( self.error, e))

    def DTMBAutoScanChannel(self):
        try:
            self.goToTunerByType('dtmb')
            self.a.input.back(3)
            time.sleep(5)
            self.a.input.menu()
            time.sleep(1)
            for i in range(5):
                self.a.input.down()
                if self.isIdFocused('auto_scan'):
                    break
            self.a.input.center()
            time.sleep(2)
            self.a.input.center()
            start_freq = self.a.ui.waitfor(id='channel_frequency').text()
            time.sleep(30)
            isScan = self.a.ui.waitfor(id='autoScanButton').text()
            mid_freq = self.a.ui.waitfor(id='channel_frequency').text()
            if start_freq == mid_freq and '停止搜台' in str(isScan):
                self.error = 'frequency is not change'
                raise Exception
            start = time.time()
            during = time.time() - start
            while 'autoScanProgress' in self.a.ui.screen().ids() and during < 360:
                print 'channel scanning...'
                time.sleep(10)
                during = time.time() - start
            self.a.input.back(2)
            time.sleep(2)
            wind = self.a.ui.window()
            if 'no_signal' in wind.ids():
                self.error = 'no channel after scan, please check if cable is plug in'
                raise Exception
            
        except Exception, e :
            raise
            
    def ATVAutoScanChannel(self):
        try:
            self.goToTunerByType('atv')
            self.a.input.back(3)
            time.sleep(5)
            self.a.input.menu()
            time.sleep(1)
            for i in range(8):
                if self.isIdFocused('auto_scan'):
                    break
                self.a.input.down()
            self.a.input.center()
            time.sleep(2)
            self.a.input.center()
            start_freq = self.a.ui.waitfor(id='channel_frequency').text()
            time.sleep(30)
            isScan = self.a.ui.waitfor(id='autoScanButton').text()
            mid_freq = self.a.ui.waitfor(id='channel_frequency').text()
            if start_freq == mid_freq and '停止搜台' in str(isScan):
                self.error = 'frequency is not change'
                raise Exception
            start = time.time()
            during = time.time() - start
            while 'autoScanProgress' in self.a.ui.screen().ids() and during < 360:
                print 'channel scanning...'
                time.sleep(10)
                during = time.time() - start
            self.a.input.back(2)
            time.sleep(2)
            wind = self.a.ui.screen()
            if 'no_signal' in wind.ids() or len(wind.ids())==6:
                self.error = 'no channel after scan, please check if cable is plug in'
                raise Exception
            
        except Exception, e :
            raise
            
    
    def goToTunerByType(self,type):
        name = ''
        if type == 'atv':
            name = '有线电视'
        elif type == 'dtmb':
            name = '地面广播数字电视'
        else:
            self.error = 'error input in goToTunerByType'
        self.launchTV()
        try:
            wind = self.a.ui.screen()
            if 'autoScanButton' in wind.ids():
                self.a.input.back()
                time.sleep(1)
                tv_type = self.a.ui.waitfor(id='tv_type_text').text()
                if name in str(tv_type):
                    for i in range(7):
                        self.a.input.up()
                        if self.isIdFocused('tv_type_text'):
                            break
                    self.a.input.center()
                    time.sleep(1)
                    if type == 'atv':
                        self.a.input.left()
                    elif type == 'dtmb':
                        self.a.input.right()
                    else:
                        pass
                    self.a.input.center()
                    time.sleep(15)
            elif 'select_btn_atv' in wind.ids() and 'select_btn_dtv' in wind.ids():
                self.a.input.left()
                self.a.input.center()
                time.sleep(15)
            elif 'port_info_content1' in wind.ids() or 'portinfo' in wind.ids():
                pass
            else:
                self.error = 'unknow page'
                raise Exception
        except Exception:
            raise Exception
    
    def isIdFocused(self,idname):
        try:
            self.a.ui.waitfor(id=idname,isFocused=True)
            return True
        except:
            return False
    
    
    def launchTV(self):
        self.a.device.sh("input keyevent 170")
        time.sleep(15)
        if 'com.letv.signalsourcemanager/com.letv.signalsourcemanager.MainActivity' not in str(self.a.ui.window()):
            self.error = 'cannot launch signal sourcemanager'
            raise Exception
    
    def isOK(self):
        time.sleep(5)
        try:
            widgets = self.a.ui.waitfor(
                anyof=[
                    self.a.ui.widgetspec(id='message', text=re.compile(r'(^Unfortunately.*stopped\.$)')),
                    self.a.ui.widgetspec(text='Wait'),
                    self.a.ui.widgetspec(id='progressBar'),
                    self.a.ui.widgetspec(id='no_signal'),])
            wid = widgets.id()
            if wid == 'message':
                self.a.input.down()
                self.a.input.center()
                self.error = "Force Closed"
                return False
            if wid == 'Wait':
                self.a.input.down()
                self.a.input.right()
                self.a.input.center()
                self.error = "ANR Happened"
                return False
            if wid == 'progressBar':
                self.error = 'loading ...'
                return False
            if wid == 'no_signal':
                self.error = 'no signal'
                return False
            self.a.log.debug("", "No Force Closed & ANR happen!")
            return True
            
        except:
            return True

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
