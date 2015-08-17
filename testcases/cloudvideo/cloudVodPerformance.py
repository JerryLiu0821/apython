# -*- coding: utf-8 -*-
'''
Created on Dec 19, 2013

@author: liujian
'''
import unittest, time, os, re, datetime
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../testcases')
import Stability, android, runtests

class TestVodPerformance(unittest.TestCase):


    def setUp(self):
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.stabdl = Stability.StabDL(self.a)
        self.error = ''
        self.id = self.setup.device_id 
        self.a.input.back(3)

    def tearDown(self):
        self.a.input.back(3)

    def testHLS_H264_1080P(self):
        """播放HLS H.264(TV版1080P频道)的详细时间|"""
        try:
            self.launchTVban()
            #go to channel page
            self.a.input.down(2)
            time.sleep(1)
            #self.a.input.left(5)
            self.a.input.right(4)
            time.sleep(1)
            #go to 1080p channel
            #self.a.input.up()
            #self.a.input.right(2)
            self.a.input.center()
            time.sleep(5)
            self.a.input.right(2)
            self.a.input.center()
            time.sleep(5)
            if "com.media.tv/com.letv.tv.activity.DetailActivity" not in self.a.ui.window():
                print 'cannot go detail activity'
                raise Exception
            if '1080P' not in str(self.a.ui.screen().texts()):
                print 'not 1080P channel'
                raise Exception
            #play
            self.a.input.center()
            time.sleep(30)
            self.a.input.back(5)
            time.sleep(2)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            """
            log_dir = './liujian/report.20140827_141517/logs/00001/logcat_main.10.58.49.172:5555.1.txt'
            """
            self.handler('hls',log_dir)
            self.a.input.home()

        except Exception, e:
            self.a.input.back(4)
            self.a.input.home()
            self.a.log.debug("", "\n testHLS_H264_0180P")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testHTTP_FLV_H264_3D(self):
        """播放HTTP FLV H.264(TV版3D频道)的详细时间|"""
        try:
            self.launchTVban()
            #go to channel page
            self.a.input.down()
            time.sleep(1)
            #self.a.input.left(5)
            self.a.input.right(4)
            time.sleep(1)
            #go to 3d channel
            #self.a.input.up(2)
            #self.a.input.right(2)
            self.a.input.center()
            time.sleep(5)
            self.a.input.center()
            time.sleep(5)
            if "com.media.tv/com.letv.tv.activity.DetailActivity" not in self.a.ui.window():
                print 'cannot go detail activity'
                raise Exception
            if '3D' not in str(self.a.ui.screen().texts()):
                print 'not 3D channel'
                raise Exception
            #play
            self.a.input.center()
            time.sleep(30)
            self.a.input.back(5)
            time.sleep(2)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            """
            log_dir = './liujian/report.20140827_183924/logs/00001/logcat_main.10.58.49.172:5555.1.txt'
            """
            self.handler('http',log_dir)
            self.a.input.home()

        except Exception, e:
            self.a.input.back(4)
            self.a.input.home()
            self.a.log.debug("", "\n testHTTP_FLV_H264_3D")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testHTTP_MP4_H264_Dolby(self):
        """播放HTTP MP4 H.264 Dolby(TV版杜比频道)的详细时间|"""
        try:
            self.launchTVban()
            #go to channel page
            self.a.input.down()
            time.sleep(1)
            #self.a.input.left(5)
            self.a.input.right(5)
            time.sleep(1)
            #go to dubi channel
            #self.a.input.up(2)
            #self.a.input.right(3)
            self.a.input.center()
            time.sleep(5)
            self.a.input.center()
            time.sleep(5)
            if "com.media.tv/com.letv.tv.activity.DetailActivity" not in self.a.ui.window():
                print 'cannot go detail activity'
                raise Exception
            #杜比: \u675c\u6bd4
            if '\u675c\u6bd4' not in str(self.a.ui.screen().texts()):
                print 'not 杜比 channel'
                raise Exception
            #play
            self.a.input.center()
            time.sleep(30)
            self.a.input.back(5)
            time.sleep(2)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            self.handler('http',log_dir)
            self.a.input.home()

        except Exception, e:
            self.a.input.back(4)
            self.a.input.home()
            self.a.log.debug("", "\n testHTTP_FLV_H264_3D")
            self.fail("Error happened: %s %s" % (self.error, e))

    def handler(self, style, log_dir):
        cloud = Stability.cloudStatus(log_dir)
        result = [] 
        self.a.log.debug("", "raise self.failureException('utp version: %s')" %(cloud.getUtpVersion()))
        output = []
        if style == 'hls':
            print 'hls vod'
            output = [
            "从用户操作到画面显示的总时长",\
            "用户播放操作    应用获取播放地址",\
            "应用获取播放地址    播放器获取播放地址",\
            "播放器获取播放地址    播放器请求解析URL(M3U8)",\
            "播放器请求解析URL(M3U8)    UTP接收播放请求",\
            "UTP接收播放请求    UTP请求调度获取下载地址",\
            "UTP请求调度获取下载地址    UTP开始下载第一个m3u8",\
            "UTP开始下载第一个m3u8    UTP开始下载第一个分片",\
            "UTP开始下载第一个分片    UTP下载完成第一个分片",\
            "播放器请求解析URL(M3U8)    播放器获取并解析URL(M3U8)完成",\
            "播放器获取并解析URL(M3U8)完成    播放器请求第一个ts分段",\
            "播放器请求第一个ts分段    开始V/A初始化",\
            "开始V/A初始化    完成V/A初始化",\
            "完成V/A初始化    播放器Prepared",\
            "播放器Prepared    播放器start",\
            "播放器start    第一帧显示时间",\
            ]
            result = cloud.vodHlsPlayProgress()
        elif style == 'http':
            print 'http vod'
            output = [
            "用户播放操作    第一帧显示时间",\
            "用户播放操作    应用获取播放地址",\
            "应用获取播放地址    播放器获取播放地址",\
            "播放器请求下载    UTP接收播放请求",\
            "UTP接收播放请求    UTP请求调度获取下载地址",\
            "UTP请求调度获取下载地址    UTP开始下载数据",\
            "UTP开始下载第一个分片    UTP下载完成第一个分片",\
            "UTP接收播放请求    开始V\A初始化",\
            "开始V\A初始化    完成A\V初始化",\
            "完成A\V初始化    播放器Prepared",\
            "播放器Prepared    播放器start",\
            "播放器start    第一帧显示时间",\
            ]
            result = cloud.vodHttpPlayProgress()

        if len(result) != len(output):
            self.error = "cannot parser log"
            raise Exception
        during = re.search("\((\d+), '(.*)'\)", result[0]).group(2)
        print during
        isError = ''
#during = int(result[0].split(":")[1].strip())
        for i in range(len(output)):
            flag, gap = re.search("\((\d+), '(.*)'\)", result[i]).groups()
            forp = ''
            if int(flag) == 0:
                forp = gap + ", 找不到 "+ output[i]
                isError +="cannot find  "+ result[i] + '; '
            elif int(flag) == 1:
               forp = gap + ", 找不到" +  output[i].split('    ')[1]
               isError +="cannot find  "+ result[i].split(':')[0].split('->')[1] + '; '
            elif int(flag) == 2:
                forp = gap + ", 找不到" +  output[i].split('    ')[0]
                isError +="cannot find  "+ result[i].split(':')[0].split('->')[0] + '; '
            else:
                forp = int(gap)

            print output[i],":", forp 
            self.a.log.debug("", "raise self.failureException('%s:%s')" %(output[i],forp)) 
        if int(during) > 1800:
            self.error = "switch time %s ms more then 1800 ms" %during
            raise Exception
        elif isError:
            self.error = isError
            raise Exception

    def launchTVban(self):
        #self.a.device.sh("am start -a android.intent.action.MAIN -n com.stv.tv/.activity.MainActivity")
        self.a.device.sh("am start -a com.letv.external.new -n com.media.tv/com.letv.tv.activity.CIBNAuthorityActivity")
        time.sleep(10)
        if "com.media.tv/com.letv.tv.activity.MainActivity" not in self.a.ui.window():
            print 'cannot go to tv ban'
            raise Exception

    def isPlaying(self):
        try:
            print 'checking'
            time.sleep(5)
            w = self.a.ui.waitfor( anyof = [
                                            self.a.ui.widgetspec(id = 'tv_loading'),
                                            self.a.ui.widgetspec(id='message')
                                            ]).id()
            if w == 'message':
                self.a.input.down()
                self.a.input.center()
                self.error=' Force close happened.'
                return False
            if w == 'tv_loading':
                self.error='tv is loading.'
                return False
        except:
            return True

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
