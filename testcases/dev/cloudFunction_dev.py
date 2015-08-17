# -*- coding: utf-8 -*-
import android, unittest, time, sys, traceback
import inspect
import re
import runtests, os, re, sys

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../testcases/')

from random import choice
import Stability


class testCloudFunction(unittest.TestCase):
    """Cloud Function Test"""
    
    def setUp(self):
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.stabdl=Stability.StabDL(self.a)
        self.id = self.setup.device_id
        self.error=""
        self.a.input.back(3)
     
    def tearDown(self):
        self.a.input.back(3)
        time.sleep(3)
    
    
    #hls
    def testVodHLS_H264_AAC_480p(self):
        """点播HLS_H264_AAC_480p|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/hls/480P/desc.m3u8"
            self.playAndHandler(url, "hls");
        except Exception,e:
            self.a.log.debug("", "\n testVodHls480p")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testVodHLS_H264_AAC_720p(self):
        """点播HLS_H264_AAC_720p|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/hls/720P/desc.m3u8"
            self.playAndHandler(url, "hls");
        except Exception,e:
            self.a.log.debug("", "\n testVodHls480p")
            self.fail("Error happened: %s %s" % (self.error, e))
        
    def testVodHLS_H264_AAC_1080p(self):
        """点播HLS_H264_AAC_1080p|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/hls/1080P/desc.m3u8"
            self.playAndHandler(url, "hls");
        except Exception,e:
            self.a.log.debug("", "\n testVodHls1080p")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testVodHLS_H264_AAC_4K3940x2160(self):
        """点播HLS_H264_AAC_4K3940x2160|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/hls/4K3940x2160/desc.m3u8"
            self.playAndHandler(url, "hls");
        except Exception,e:
            self.a.log.debug("", "\n testVodHls4K3940x2160")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testVodHLS_H264_AAC_4K4096x2160(self):
        """点播HLS_H264_AAC_4K4096x2160|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/hls/4K4096x2160/desc.m3u8"
            self.playAndHandler(url, "hls");
        except Exception,e:
            self.a.log.debug("", "\n testVodHls4K3940x2160")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testVodHLS_H264_Dolby_1080(self):
        """点播HLS_H264_Dolby_1080|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/hls/dolby-1080/desc.m3u8"
            self.playAndHandler(url, "hls");
        except Exception,e:
            self.a.log.debug("", "\n testVodHls4K3940x2160")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testVodHLS_H264_DTS_1080(self):
        """点播HLS_H264_DTS_1080|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/hls/dts-1080/desc.m3u8"
            self.playAndHandler(url, "hls");
        except Exception,e:
            self.a.log.debug("", "\n testVodHls4K3940x2160")
            self.fail("Error happened: %s %s" % (self.error, e))
    #end hls    
    
    #http
    def testVodHTTP_MP4_H264_480P(self):
        """点播HTTP_MP4_H264_480P|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/http/HTTP_MP4_H264_480P.mp4"
            self.playAndHandler(url, "http");
        except Exception,e:
            self.a.log.debug("", "\n testVodHTTP_MP4_H264_480P")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testVodHTTP_MP4_H264_720P(self):
        """点播HTTP_MP4_H264_720P|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/http/HTTP_MP4_H264_720P.mp4"
            self.playAndHandler(url, "http");
        except Exception,e:
            self.a.log.debug("", "\n testVodHTTP_MP4_H264_720P")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testVodHTTP_MP4_H264_1080P(self):
        """点播HTTP_MP4_H264_1080P|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/http/HTTP_MP4_H264_1080P.mp4"
            self.playAndHandler(url, "http");
        except Exception,e:
            self.a.log.debug("", "\n testVodHTTP_MP4_H264_1080P")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testVodHTTP_FLV_H264_720P(self):
        """点播HTTP_FLV_H264_720P|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/http/HTTP_FLV_H264_720P.flv"
            self.playAndHandler(url, "http");
        except Exception,e:
            self.a.log.debug("", "\n testVodHTTP_FLV_H264_720P")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testVodHTTP_FLV_H264_1080P(self):
        """点播HTTP_FLV_H264_1080P|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/http/HTTP_FLV_H264_1080P.flv"
            self.playAndHandler(url, "http");
        except Exception,e:
            self.a.log.debug("", "\n testVodHTTP_FLV_H264_1080P")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testVodHTTP_MP4_H265_480P(self):
        """点播HTTP_MP4_H265_480P|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/http/HTTP_MP4_H265_480P.mp4"
            self.playAndHandler(url, "http");
        except Exception,e:
            self.a.log.debug("", "\n testVodHTTP_MP4_H265_480P")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testVodHTTP_MP4_H265_720P(self):
        """点播HTTP_MP4_H265_720P|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/http/HTTP_MP4_H265_720P.mp4"
            self.playAndHandler(url, "http");
        except Exception,e:
            self.a.log.debug("", "\n testVodHTTP_MP4_H265_720P")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testVodHTTP_MP4_H265_1080P(self):
        """点播HTTP_MP4_H265_1080P|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/http/HTTP_MP4_H265_1080P.mp4"
            self.playAndHandler(url, "http");
        except Exception,e:
            self.a.log.debug("", "\n testVodHTTP_MP4_H265_1080P")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testVodHTTP_MP4_H265_4K(self):
        """点播HTTP_MP4_H265_4K|"""
        try:
            url = "http://10.154.250.32:8080/live/cloudvideo_function/http/HTTP_MP4_H265_4K.mp4"
            self.playAndHandler(url, "http");
        except Exception,e:
            self.a.log.debug("", "\n testVodHTTP_MP4_H265_4K")
            self.fail("Error happened: %s %s" % (self.error, e))
    #end http
            
    def playAndHandler(self, url, type):
        self.stabdl.open_intent("Filesystem")
        time.sleep(5)
        cmd = "am start -a android.intent.action.VIEW -d \'%s\' -n com.letv.videoplayer/.MainActivity" %url
        self.a.device.sh(cmd)
        time.sleep(10)
        self.operation()
        self.a.input.back()
        time.sleep(20)
        print "start to handle logcat"
        log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
        cutlog = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'cutplaylogcat.txt')
        
        setdatasource = r'.*MediaPlayerService:\ \[\d+\]\ setDataSource\(%s\)\s*' %url
        first_frame = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 3,\ 0\)'
        
        # find start to play
        fo = open(log_dir, "r+")
        fld = fo.readlines();
        fo.close()
        setdataindex = len(fld)
        firstframe = len(fld)
        for i in fld:
            if re.compile(setdatasource).match(i):
                setdataindex = fld.index(i)
                for j in fld[setdataindex:]:
                    if re.compile(first_frame).match(j):
                        firstframe = fld.index(j)
                        break
                break
        
        fw = open(cutlog,"a+")
        fw.writelines(fld[setdataindex:])
        fw.close()
        
        cloud = Stability.cloudStatus(cutlog)
        playerror = cloud.playerError()
        duration = cloud.getPlayDuration()
        resolution = cloud.getResolution()
        playstatus = cloud.checkVodPlayStatus()
        seekstatus = ""
        if type == "hls":
            seekstatus = cloud.checkVodHlsSeekStatus()
        elif type =="http":
            seekstatus = cloud.checkVodHttpSeekStatus()
        pausestatus = cloud.checkVodPauseStatus()
        stopstatus = cloud.checkVodStopStatus()
        self.a.log.debug("", "raise self.failureException('播放视频: %s')" %url)
        self.a.log.debug("", "raise self.failureException('Mediaplayer Error次数: %s')" %playerror)
        self.a.log.debug("", "raise self.failureException('Duration: %s')" %duration)
        self.a.log.debug("", "raise self.failureException('Resolution: %s')" %resolution)
        self.a.log.debug("", "raise self.failureException('seek 是否成功: %s')" %seekstatus)
        self.a.log.debug("", "raise self.failureException('pause是否成功: %s')" %pausestatus)
        self.a.log.debug("", "raise self.failureException('exit是否成功: %s')" %stopstatus)
        fail = False
        if playerror !=0:
            self.error += "player error: %s; " %playerror
            fail = True
        elif not seekstatus: 
            fail = True
            self.error += "seek failed; "
        elif not pausestatus: 
            fail = True
            self.error += "pause failed; "
        elif not stopstatus:
            fail = True
            self.error = "stop failed; "
        if fail: raise Exception
        
    def operation(self):
        time.sleep(10)
        print "right 5 times"
        self.a.input.right(5)
        time.sleep(10)
        print "sleep 10s"
        self.a.input.center()
        time.sleep(10)
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
