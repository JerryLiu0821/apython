# -*- coding: utf-8 -*-
import android, unittest, time, sys, traceback
sys.path.append('../testcases')
import Stability

from random import choice
import datetime
import runtests
import os



class testScreenShot(unittest.TestCase):

    def setUp(self):
        try :

            self.error = ''
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.stabdl = Stability.StabDL(self.a)
            self.id = self.setup.device_id  
            self.path = "/mnt/sdcard/Pictures/Screenshots"
            self.a.input.back(3)
        except :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        self.a.input.back(3)
        
    def checkPhoto(self):
        photoList = self.a.device.sh("ls %s" %self.path)
        print photoList
        today = datetime.date.today().strftime('%Y-%m-%d')
        if today in str(photoList):
            return True
        return False
            
    def testShutScreen(self):
        '''超遥分享键截图|超遥分享键截图'''
        try:
            self.a.device.sh("input keyevent 4415")
            time.sleep(10)
            if not self.checkPhoto():
                self.error = "failed to capture the photo"
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testShutScreen")
            self.fail("Error happened: %s %s" % (self.error, e))
            
if __name__ == '__main__':
    unittest.main()



