# -*- coding: utf-8 -*- 
'''
Created on Mar 11, 2014

@author: jerry
'''
import unittest
import time, re, random
import Stability


class TestSourceSwitch(unittest.TestCase):
    
    def setUp(self):
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.id = self.setup.device_id
        self.error=''
        self.source = {'Tuner':170, 'VGA':4401, 'CVBS':4402, 'HDMI':269}
        self.a.input.back(3)


    def tearDown(self):
        pass

    def testSwitchSourceByList(self):
        """信号源列表切换信号源|按遥控器的列表键选择信号源"""
        try:
            self.a.device.sh('input keyevent %s' %self.source['VGA'])
            time.sleep(20)
            for i in range(6):
                self.a.device.sh('input keyevent 257')
                time.sleep(2)
                self.a.input.down()
                time.sleep(1)
                self.a.input.center()
                time.sleep(20)
                if not self.isOK('down'):
                    raise Exception
            
        except Exception, e:
            self.a.log.debug("", "\n testSwitchSourceByList")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    def testSwitchSourceBySource(self):
        """信号源键切换信号源|按遥控器的信号源键选择信号源"""
        try:
            self.a.device.sh('input keyevent %s' %self.source['VGA'])
            time.sleep(20)
            for i in range(6):
                times = random.randint(2,10)
                for i in range(times):
                    self.a.device.sh('input keyevent 4404')
                    time.sleep(1)
                self.a.input.center()
                time.sleep(20)
                if not self.isOK('source'):
                    raise Exception
            
        except Exception, e:
            self.a.log.debug("", "\n testSwitchSourceBySource")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    def testSwitchSourceByKey(self):
        """四大天王键切换信号源|按遥控器的信号源快捷键切换信源"""
        try:
            for type in self.source.keys():
                #type = random.choice(self.source.keys())
                print type
                self.a.device.sh('input keyevent %s' %self.source[type])
                time.sleep(20)
                if not self.isOK(type):
                    raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testSwitchSourceByKey")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    def isOK(self,type):
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
                self.error = "Force Closed after press %s" %type
                return False
            if wid == 'Wait':
                self.a.input.down()
                self.a.input.right()
                self.a.input.center()
                self.error = "ANR Happened after press %s " %type
                return False
            if wid == 'progressBar':
                self.error = 'loading ... after press %s ' %type
                return False
            if wid == 'no_signal':
                self.error = 'no signal after press %s ' %type
                return False
            self.a.log.debug("", "No Force Closed & ANR happen!")
            return True
            
        except:
            return True

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
