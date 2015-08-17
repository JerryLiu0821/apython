# -*- coding: utf-8 -*-
import android, unittest, time, sys, traceback
import Stability
import inspect
from random import choice

import runtests
import re, os



class testLivePlay(unittest.TestCase):
    """Live_Play """

    def setUp(self):
        try :
            #self.playtime = 1*60*60 # play 'playtime' seconds for each video
            self.playtime = 2
            self.temPlaytime = 2
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.error=''
            self.stabdl=Stability.StabDL(self.a)
            self.id = self.setup.device_id 
            self.a.input.back(3)
        except Exception, e :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        self.a.input.back(3)
    
          
    def testChangLiveChannelByChannelupKey(self):
        """ 直播台切换 | 直播台遍历"""
        try:
            self.changLiveChannelByChannelupKey(40, 2)           
        except Exception, e :
            self.a.log.debug("", "\n testStabLetvUpToDownSomeChannel")
            self.fail("Error happened: %s %s" % ( self.error, e))

    def launchLetv(self):
        for i in range(3):
            self.a.input.home()
            time.sleep(5)
        self.a.input.back(2)
        time.sleep(2)
        for i in range(5):
            if 'com.letv.signalsourcemanager/com.letv.signalsourcemanager.MainActivity' not in str(self.a.ui.window()):
                self.a.input.home()
                time.sleep(2)
                self.a.input.left()
                time.sleep(1)
                self.a.input.center()
            else:
                break
        self.a.input.home()
        time.sleep(2)
        self.a.input.right(2)
        self.a.input.center()
            
    def isPlaying(self):
        try:
            time.sleep(5)
            w = self.a.ui.waitfor( anyof = [
                                            self.a.ui.widgetspec(id = 'tv_loading'),
                                            self.a.ui.widgetspec(id='message', text=re.compile(r'(^Unfortunately.*stopped\.$)'))       
                                            ]).id()
            if w == 'message':
                self.a.input.down()
                self.a.input.center()
                self.error=' Force close happened.'
                return False
            if w == 'tv_loading':
                self.a.log.debug("","Error: This channel can not be played, pls check the network status.")
                self.error='Error: This channel can not be played, pls check network status.'
                return False
        except:
            return True 

    
    def changLiveChannelByChannelupKey(self,times, playtimes):
        for i in range(times):
            self.a.input.channel_up()
            time.sleep(playtimes)
            if not self.isPlaying():
                raise Exception
            
    def changLiveChannelByChanneldownKey(self,times, playtimes):
        for i in range(times):
            self.a.input.channel_down()
            time.sleep(playtimes)
            if not self.isPlaying():
                raise Exception
            
    def changeChannelUpToDown(self, times, playtime):
          self.a.input.center()
          time.sleep(5)
          for i in range(times):
              self.a.input.up()
              time.sleep(1)
              if not self.isPlaying():
                  raise Exception
          

if __name__ == '__main__':
    unittest.main()


