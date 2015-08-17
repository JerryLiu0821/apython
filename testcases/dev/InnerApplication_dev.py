# -*- coding: utf-8 -*-
'''
Created on Oct 16, 2013

@author: liujian
'''
import unittest
import runtests
import time

import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
sys.path.append('../testcases')
import Stability
class TestInnerApplication(unittest.TestCase):


    def setUp(self):
        self.error = ""
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.id = self.setup.device_id
        self.a.input.back(3)


    def tearDown(self):
        self.a.input.back(3)

    def launchCNTV(self):
        try:
            act = 'android.intent.action.MAIN' 
            cat = 'android.intent.category.LAUNCHER' 
            flg = '0x10200000' 
            cmpp = 'tv.icntv.ott/.icntv'
            cmd = 'am start -a %s -c %s -f %s -n %s' %(act, cat, flg, cmpp)
            self.a.device.sh(cmd)
            start_times = time.time()
            #wind = 'tv.icntv.ott/tv.icntv.ott.icntv'
            time.sleep(1)
            during = time.time() - start_times
            while 'start_showing' in self.a.ui.screen().ids() and during < 300:
                print 'loading cntv...'
                during = time.time() - start_times
            print during
            return during
        except:
            self.error = 'launch CNTV failed'
            return -1
    def exitCNTV(self):
        try:
            for i in range(6):
                self.a.input.back()
                time.sleep(1)
                w = self.a.ui.screen()
                if 'alert_content' in w.ids():
                    self.a.input.left()
                    self.a.input.center()
                    break
        except:
            self.error = 'cannot close cntv'
            self.a.input.home()
            
    
    def _testLaunchCNTVTime(self):
        """CNTV启动时间|操作步骤：;1. 启动CNTV"""
        try:
            times = self.launchCNTV()
            self.a.log.debug("", "raise self.failureException('CNTV启动时间: %.3f s')" %times)
            self.exitCNTV()
        except Exception, e:
            runtests.log_screenshot(self.a, '', 'fail_testLaunchCNTVTime', 'testNetworkTesting')
            self.a.log.debug("", "\n testLaunchCNTVTime")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testNetworkTesting(self):        
        """网络测速|操作步骤:;1. 设置中进行网络测试"""
        try:
            self.a.device.sh("input keyevent 176")
            time.sleep(2)
            self.a.input.up()
            self.a.input.left(8)
            self.a.input.down()
            self.a.input.right(2)
            self.a.input.center()
            time.sleep(2)
            w = self.a.ui.screen()
            if 'title' not in w.ids():
                self.error = 'cannot enter network page'
                raise Exception
            self.a.input.center()
            time.sleep(5)
            
            start_time = time.time()
            during = time.time()-start_time
            while 'text_cur_speed' in self.a.ui.screen().ids() and during < 180:
                print 'network testing ...'
                time.sleep(5)
                during = time.time() - start_time
            if during >= 120:
                self.error = 'network testing timeout'
                runtests.log_screenshot(self.a, '', 'fail_testNetworkTesting', 'testNetworkTesting')
                raise Exception
            try:
                l = self.a.ui.waitfor(id='text_speed').text()
                print '平均速度：%s' %l
                self.a.log.debug("", "raise self.failureException('网络平均速度: %s')" %l)
            except:
                self.error = 'cannot get speed'
                runtests.log_screenshot(self.a, '', 'fail_testNetworkTesting', 'testNetworkTesting')
                raise Exception
            self.a.input.back(4)
        except Exception, e:
            self.a.log.debug("", "\n testNetworkTesting")
            self.fail("Error happened: %s %s" % (self.error, e))
        
    
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
