# -*- coding: utf-8 -*-
'''
Created on Apr 17, 2014

@author: liujian
'''
import android, unittest, time, sys, traceback
import inspect
import re, os, commands
import sys
sys.path.append('../testcases')
import Stability

class TestRemoteUpgrade(unittest.TestCase):


    def setUp(self):
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.id = self.setup.device_id
        self.error = ''
        self.timeout=1800
        os.system('adb -s %s logcat -c' %self.id)


    def tearDown(self):
        pass

    def testRemoteUpgrade(self):
        """遥控器升级|模拟升级遥控器操作"""
        try:
            self.a.device.sh('am broadcast -a com.letv.input_nanosic')
            time.sleep(5)
            if 'com.letv.letvremoterupdate/com.letv.letvremoterupdate.UpdateActivity' not in self.a.ui.window():
                self.error = 'cannot launch remote upgrade activity'
                raise Exception
            self.a.input.down()
            self.a.input.left(2)
            self.a.input.center()
            time.sleep(2)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            print log_dir
            flag = True
            while flag :
                status,output = commands.getstatusoutput('grep \'str progress\' %s |tail -1'%log_dir)
                print output
                if 'str progress= 1.000' in output:
                    s,o = commands.getstatusoutput('grep \'remoter update success\' %s'%log_dir)
                    if not s:
                        print o
                        flag = False
                time.sleep(5)
                
        except Exception,e:
            self.a.log.debug("", "\n testRemoteUpgrade")
            self.fail("Error happened: %s %s" % (self.error, e))
        
        
    def upgrade_progress(self):
        try:
            w = self.a.ui.screen()
            if 'progress_doing' in w.ids() and 'progress_complete' not in w.ids():
                print w.texts()[1][2]
                if '100%' in w.texts()[1][2]:
                    return False
                else:
                    return True
            else:
                return True
        except:
            print 'upgrade activity is not on front' 
            return False

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
