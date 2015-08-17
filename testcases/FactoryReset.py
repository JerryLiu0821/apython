# -*- coding: utf-8 -*-
import android, unittest, time, sys, traceback
import Stability
import inspect
from random import choice

import runtests
import re,os,random



class testFactoryReset(unittest.TestCase):
    """Live_Play """

    def setUp(self):
        try :
            #self.playtime = 1*60*60 # play 'playtime' seconds for each video
            self.playtime = 2
            self.temPlaytime = 2
            self.channel_num = 54
            self.temPlaytime = 2
            self.outloop = 1
            self.loop_channel_num = 17
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.error=''
            self.stabdl=Stability.StabDL(self.a) 
            self.id= self.setup.device_id        
            self.a.input.back(3)
            #self.pullDataLogs()
            #self.isPlaying()
            

        except Exception, e :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        try :
            runtests.log_screenshot(self.a, '', 'screenshot', 'Liveplay')
        except:
            pass

    def pullDataLogs(self):
            abs_path = os.path.join(android.log.report_directory(), android.log.logs_directory())
            cmd ='adb -s %s pull /data/Logs/Log.0  %s'%(self.id, abs_path)
            os.system (cmd)
            
    def testFactoryReset(self):
        """恢复出场设置 |操作步骤：;1. 恢复出场设置"""
        try:
            self.a.device.sh("input keyevent 176")
            self.a.input.left(8)
            self.a.input.right(4)
            time.sleep(2)
            self.a.input.right()
            self.a.input.center()
            self.a.input.down(20)
            w=self.a.ui.screen()
            if "reset" in w.ids():
                self.a.input.center()
                self.a.input.down()
                self.a.input.center()
                time.sleep(300)
                os.system('adb disconnect '+ self.id )
                os.system('adb connect '+ self.id )
                time.sleep(2)
                os.system('adb -s %s root'%self.id)
                time.sleep(2)
                os.system('adb connect '+ self.id)
                os.system('adb connect '+ self.id)
                self.a.input.back()
                time.sleep(2)
                self.a.input.left()
                self.a.input.center()
                time.sleep(10)      
            else:
                raise Exception      
                        
        except Exception, e :
            self.a.log.debug("", "\n testFactoryReset")
            self.fail("Error happened: %s %s" % ( self.error, e))
            

    

if __name__ == '__main__':
    unittest.main()


