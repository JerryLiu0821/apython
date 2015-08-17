# -*- coding: utf-8 -*-
import android, unittest, time, sys, traceback
import inspect
import re
import runtests
sys.path.append('../testcases')
import Stability
from random import choice


class testLocalPlayByTypes(unittest.TestCase):
    """LocalPlay """

    outloop = 1
    playtime = 10 # play 'playtime' seconds for each video
    
    def setUp(self):
        try :
            #self.loop = 1  
            self.play_urls=[]
            self.error_urls = []
            self.error=""
            self.start_over = 1
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.stabdl=Stability.StabDL(self.a)   
            self.pf=Stability.PlayFiles(self.a, self.playtime) 
            self.a.input.back(3)

        except Exception, e:
            self.a.log.debug("", "\n Set up")
            
     
    def tearDown(self):
        try :
            self.a.input.back(3)
            #self.a.home.home()
            time.sleep(3)
        except :
            self.a.log.debug("", "\n Tear down")

    def testPlayTheFolderVideos(self):
        "播放所有格式的视频文件|操作步骤:;1. play video in smoke_MutilMedia folder in storage"
        try :
            #start filemanager
            self.a.device.sh(" am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -f 0x10200000 -n com.letv.filemanager/.FileExplorerTabActivity")
            time.sleep(4)
            self.playFiles('/mnt/usb/sda1/smoke_MultiMedia', 'f')
        except Exception, e :
            self.a.log.debug("", "\n testPlayTheFolderVideos")
            self.fail("Error happened while playing videos. Error URL: %s" % ( str(self.error_urls)))
    

    def getPlayFiles(self,folder_path,media_type):
        media_files = self.a.device.sh("busybox find %s -type %s" %(folder_path, media_type))
        media_file=str(media_files)
        media_list = media_files.split("\r\n")
        l = len(media_list)
        self.play_urls=[]
        for i in range(0, l-1):
            self.play_urls.append('file://' + media_list[i])
        print "all files: %s" %len(self.play_urls)
            
    def playFiles(self, folder_path, Media_Type):
        self.getPlayFiles(folder_path, Media_Type)
        self.loop=len(self.play_urls)   
        #self.loop=1   
        for j in range(1, self.outloop+1):
            for i in range (0,self.loop):
                print "play: %s" %self.play_urls[i]
                cmd = "am start -a android.intent.action.VIEW -d \'%s\' -n com.letv.videoplayer/.MainActivity" %self.play_urls[i]
                #cmd = "am start -n letv.lcworld.player/.MainActivity -d \'%s\' -a android.intent.action.VIEW"%self.play_urls[i]
                self.a.device.sh(cmd)
                time.sleep(5)
                runtests.log_screenshot(self.a, '', self.play_urls[i], 'playfiles')
                if self.isNoError(): # Playing right
                    self.a.log.debug("","This link: %s is played successfully."%self.play_urls[i])
                    self.seek()
                    self.a.input.back()
                    
                else:  # Playing error
                    self.error_urls.append(self.play_urls[i])
                    print "Failed: %s" %self.play_urls[i]
                    self.a.log.debug("","Error: %s This link can not be played."%self.play_urls[i])                   
                
                time.sleep(1)
                                          
            self.a.input.back(2)
            time.sleep(5)
        if self.error_urls!=[]:
            raise Exception
        
    def seek(self):
        time.sleep(5)
        print "right 3 times"
        self.a.input.right(3)
        time.sleep(5)
        print "letf 2 times"
        self.a.input.left(2)
        time.sleep(5)
        print "sleep 10s"
        self.a.input.center()
        time.sleep(5)
        print "start to play"
        self.a.input.center()
        time.sleep(10)
        
    def isNoError(self):
        try:
            w = self.a.ui.waitfor(anyof=[
                self.a.ui.widgetspec(id="message"),
                self.a.ui.widgetspec(id="player_error_info_tv"),
                self.a.ui.widgetspec(id='player_error_iv'),
                ])
            w_id=w.id()
            if(w_id=="message"):
                self.error="ANR happeded"
                self.a.input.down()
                time.sleep(1)
                self.a.input.right(2)
                self.a.input.center()  #Click the OK on "Can't play video" dialog.
                time.sleep(1)
                self.error_urls.append('ANR happened')
                return False
            if(w_id=="player_error_info_tv"):
                self.error="can not play this file"
                time.sleep(2)
                self.error_urls.append('cannot play')
                return False
            return True
            
        except:
            return True


if __name__ == '__main__':
    unittest.main()


