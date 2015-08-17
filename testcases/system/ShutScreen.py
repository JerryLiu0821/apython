# -*- coding: utf-8 -*-
import android, unittest, time, sys, traceback
sys.path.append('../testcases')
import Stability

from random import choice
import datetime
import runtests
import os



class testShutScreen(unittest.TestCase):

    def setUp(self):
        try :

            self.error = ''
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.stabdl = Stability.StabDL(self.a)
            self.id = self.setup.device_id   
            self.a.input.back(3)
        except :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        self.a.input.back(3)
            
    def testShutScreen(self):
        '''反复关闭打开电视屏幕|反复关闭打开电视屏幕'''
        self.jar = "UiAutomator.jar"
        #self.jar = "UiAutomator.jar"
        self.case = "com.letv.settings.TestShutScreen"
        try:
            #self.a.device.sh("rm -rf %s/*" %self.path)
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            
            if result != 'PASS':
                self.error = str(info)
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testShutScreen")
            self.fail("Error happened: %s %s" % (self.error, e))
            
if __name__ == '__main__':
    unittest.main()



