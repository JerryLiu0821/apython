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

    def setUp(self):
        try :
            self.error=""
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            #self.path = "/mnt/usb/sda1/smoke_MultiMedia"
            self.path = "/mnt/usb/sda1/three"
            self.meidaType = None
            self.results = {}
            self.a.input.back(3)

        except Exception, e:
            self.a.log.debug("", "\n Set up")


    def tearDown(self):
        try :
            self.a.input.back(3)
            time.sleep(3)
        except :
            self.a.log.debug("", "\n Tear down")

    def testPlayTheFolderVideos(self):
        "播放所有格式的视频文件|操作步骤:;1. play video in smoke_MutilMedia folder in storage"
        try :
            #start filemanager
            self.a.device.sh(" am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -f 0x10200000 -n com.letv.filemanager/.FileExplorerTabActivity")
            time.sleep(4)
            urls = self.getPlayFiles(self.path, self.mediaType)
            for url in urls:
                self.playFile(url);
            
            for key in self.results.keys():
                print key, "\t", self.results[key]
            
        except Exception, e :
            self.a.log.debug("", "\n testPlayTheFolderVideos")
 

    def getPlayFiles(self,folder_path,media_type):
        print "getplayfiles"
        if media_type != None:
            media_files = self.a.device.sh("busybox find %s -type f |grep %s" %(folder_path, media_type))
        else:
            media_files = self.a.device.sh("busybox find %s -type f" %(folder_path))
        media_list = media_files.split("\r\n")
        play_urls=[]
        for i in range(0, len(media_list)-1):
            play_urls.append('file://' + media_list[i])
        return play_urls
        
            
    def playFile(self, url):
        print "play ", url
        cmd = "am start -a android.intent.action.VIEW -d \'%s\' -n com.letv.videoplayer/.MainActivity" %url
        self.a.device.sh(cmd)
        time.sleep(10)
        runtests.log_screenshot(self.a, '', url, 'playfiles')
        w = self.a.ui.screen()
        status = "successfully"
        if "file_browse_frame" in w.ids():
            print "type error"
            status =  "type error"
        elif "player_error_info_tv" in w.ids():
            print "cannot play"
            status =  'cannot play'
        else:
            print "play successfully"
            pass
        self.results[url] = status
        self.a.input.back()
        time.sleep(3)

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
                return False
            if(w_id=="player_error_info_tv"):
                self.error="can not play this file"
                time.sleep(2)
                return False
            return True

        except:
            return True


if __name__ == '__main__':
    unittest.main()


