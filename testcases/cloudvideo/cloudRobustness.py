# -*- coding: utf-8 -*-
import android, unittest, time, sys, traceback
import inspect
import re
import runtests, os, re, sys,datetime

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../testcases')
import Stability
from random import choice


class testCloudRobustness(unittest.TestCase):
    """Cloud Robustness Test"""

    def setUp(self):
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.stabdl=Stability.StabDL(self.a)
        self.id = self.setup.device_id
        self.error=""
        self.a.input.back(3)
        cmd = 'am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -f 0x10200000 -n com.letv.filemanager/.FileExplorerTabActivity'
        self.a.device.sh(cmd)
        time.sleep(5)

    def tearDown(self):
        self.a.input.back(3)
        time.sleep(3)

    #Redirect
    def testVodHLS_M3U8_Redirect(self):
        """点播HLS_M3U8_Redirect|"""
        try:
            url = 'http://10.154.250.32:8080/live/cloudvideo_robustness/compatibility/m3u8_302.m3u8'
            cmd = 'am start -a android.intent.action.VIEW -d \'%s\' -n com.stv.videoplayer/.MainActivity' %url
            self.a.device.sh(cmd)
            time.sleep(30)
            if not self.isNoError():
                raise Exception 
            
        except Exception,e:
            self.a.log.debug("", "\n testVodHls480p")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testVodHLS_Slice_Redirect(self):
        """点播HLS_Slice_Redirect|"""
        try:
            url = 'http://10.154.250.32:8080/live/cloudvideo_robustness/compatibility/ts_302.m3u8'
            cmd = 'am start -a android.intent.action.VIEW -d \'%s\' -n com.stv.videoplayer/.MainActivity' %url
            self.a.device.sh(cmd)
            time.sleep(30)
            if not self.isNoError():
                raise Exception 
            
        except Exception,e:
            self.a.log.debug("", "\n testVodHls480p")
            self.fail("Error happened: %s %s" % (self.error, e))


    def testVodScreenRateChange(self):
        """点播标清-高清-1080P-4K分辨率视频|"""
        try:
            url = 'http://10.154.250.32:8080/live/cloudvideo_robustness/protocol/videosize/desc.m3u8'
            cmd = 'am start -a android.intent.action.VIEW -d \'%s\' -n com.stv.videoplayer/.MainActivity' %url
            self.a.device.sh(cmd)
            time.sleep(30)
            if not self.isNoError():
                raise Exception 

        except Exception,e:
            self.a.log.debug("", "\n testVodHls480p")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testVodLargeFirstSliceStartTime(self):
        """首切片20M资源起播时间|"""
        try:
            url = 'http://10.154.250.32:8080/live/cloudvideo_robustness/protocol/vod/first-20m.m3u8'
            cmd = 'am start -a android.intent.action.VIEW -d \'%s\' -n com.stv.videoplayer/.MainActivity' %url
            self.a.device.sh(cmd)
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            during = self.playerPrepareTime(log_dir)
            print during
            self.a.log.debug("", "raise self.failureException('首切片20M资源起播时间: %s ms')" % during)
            if during == -1:
                self.error = 'parse error'
                raise Exception
            if during > 2000:
                self.error = 'live player prepare time more then 2000ms'
                raise Exception

        except Exception,e:
            self.a.log.debug("", "\n testVodHls480p")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testVodThreeSliceStartTime(self):
        """首3个分片各1.5s资源起播时间|"""
        try:
            url = 'http://10.154.250.32:8080/live/cloudvideo_robustness/protocol/vod/3xsmall.m3u8'
            cmd = 'am start -a android.intent.action.VIEW -d \'%s\' -n com.stv.videoplayer/.MainActivity' %url
            self.a.device.sh(cmd)
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            during = self.playerPrepareTime(log_dir)
            print during
            self.a.log.debug("", "raise self.failureException('首3个分片各1.5s资源起播时间: %s ms')" % during)
            if during == -1:
                self.error = 'parse error'
                raise Exception
            if during > 2000:
                self.error = 'live player prepare time more then 2000ms'
                raise Exception

        except Exception,e:
            self.a.log.debug("", "\n testVodHls480p")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testVodLargeSmallSliceLoading(self):
        """2s和20s分片间隔资源播放是否loading|"""
        try:
            url = 'http://10.154.250.32:8080/live/cloudvideo_robustness/protocol/vod/2x20.m3u8'
            cmd = 'am start -a android.intent.action.VIEW -d \'%s\' -n com.stv.videoplayer/.MainActivity' %url
            self.a.device.sh(cmd)
            time.sleep(180)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            start_pattern = re.compile(r'.*MediaPlayerService:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 701,\ 0\)')
            end_pattern = re.compile(r'.*MediaPlayerService:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 702,\ 0\)')
            loading_list = self.recode_analysis(log_dir, start_pattern, end_pattern)
            loading_times = 0
            if loading_list ==[]:
                print 'no loading during playing'
                
            else:
                times = len(loading_list)/5 if len(loading_list)%5==0 else len(loading_list)/5 + 1
                print '\n'
                print 'laoding times: %s' %times
                loading_times = times
                
                sum = 0.0
                
                #print loading time
                for x in range(1, times+1):
                    if x*5-1 < len(loading_list):
                        sum +=  loading_list[x*5-1]
                        print loading_list[x*5-1]
                print 'average loading time is: %s ms' %(sum/(len(loading_list)/5) if len(loading_list)/5 != 0 else -1)
            
            self.a.log.debug("", "raise self.failureException('播放三分钟loading的次数为: %s 次')" % loading_times)

            if loading_times != 0:
                self.error = 'loading %s times' %loading_times
                raise Exception

        except Exception,e:
            self.a.log.debug("", "\n testVodHls480p")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testVodNoExinfSeek(self):
        """M3U8无#EXTINF资源|播放正常不能seek"""
        try:
            url = 'http://10.154.250.32:8080/live/cloudvideo_robustness/protocol/vod/no_extinf.m3u8'
            cmd = 'am start -a android.intent.action.VIEW -d \'%s\' -n com.stv.videoplayer/.MainActivity' %url
            self.a.device.sh(cmd)
            time.sleep(30)
            if not self.isNoError():
                raise Exception
            self.a.input.right(10)
            time.sleep(10)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            cloud = Stability.cloudStatus(log_dir)
            seekstatus = cloud.checkVodHlsSeekStatus()
            if seekstatus:
                self.error = 'seek successfully'
                raise Exception

        except Exception,e:
            self.a.log.debug("", "\n testVodHls480p")
            self.fail("Error happened: %s %s" % (self.error, e))

    def playerPrepareTime(self, logdir):
        """ param: log file directory
            func: if player prepare ok then return ms for player prepare time else return -1
            """
        get_list_start = ''
        get_list_end = ''
        pattern_start = re.compile(r'.*MediaPlayerService.*Client\((\d+)\)\ constructor')
        fp = open(logdir, 'r')
        all_lines = fp.readlines()
        fp.close()
            
        pipeline = 1
        for line in all_lines:
            match_start = pattern_start.match(line)
            if match_start:
                pipeline = match_start.group(1)
                get_list_start = match_start.group()
            #pattern_end = re.compile(r'.*MediaPlayerService.*:\ \[%s\] notify\ \(\w+,\ 1,\ 0,\ 0\)' % pipeline)
            pattern_end = re.compile(r'.*MediaPlayerService.*:\ \[%s\] start\ done' % pipeline)
            
            match_end = pattern_end.match(line)
            if match_end:
                get_list_end = match_end.group()
        print get_list_start
        print get_list_end
            
        if get_list_start == '' or get_list_end == '':
            self.error = 'cannot play after 30s'
            return -1
            
        """_start_time = get_list_start.split()[1][6:]
        _end_time = get_list_end.split()[1][6:]
        start_time = _start_time.split('.')
        end_time = _end_time.split('.')
        during = (int(end_time[0]) * 1000 + int(end_time[1])) - (int(start_time[0]) * 1000 + int(start_time[1]))"""
        during = self.calculator(get_list_start[:18], get_list_end[:18])
        print during
        return during

    def calculator(self, start_str, end_str):
        """ calculator time between strings like format 12-19 17:31:34.166
            return float like 2390 ms"""
        year = datetime.datetime.today().year
        
        start = start_str.split('.')
        end = end_str.split('.')
        start[0] = str(year) + '-' + start[0]
        end [0] = str(year) + '-' + end[0]
        
        toTime_start = time.mktime(time.strptime(start[0], '%Y-%m-%d %H:%M:%S'))
        toTime_end = time.mktime(time.strptime(end[0], '%Y-%m-%d %H:%M:%S'))
        s = int(toTime_end - toTime_start)
        if int(end[1]) < int(start[1]):
            s -= 1
            end[1] = '1' + end[1]
        ms = int(end[1])*0.001 - int(start[1])*0.001
        return int(s*1000 + ms*1000)

    def recode_analysis(self, filename, start_pattern, end_pattern):
        fp = open(filename, 'r')
        all_lines = fp.readlines()
        fp.close()
            
        loading = []
        start = []
        end = []
        for i in range(len(all_lines)):
            match_start = start_pattern.match(all_lines[i])
            match_end = end_pattern.match(all_lines[i])
            if match_start:
                #start.append(str(i) + " " +all_lines[i].strip(os.linesep))
                start.append(all_lines[i])
            elif match_end:
                #end.append(str(i) + " " +all_lines[i].strip(os.linesep))
                end.append(all_lines[i])
        if start == [] or end == []:
            return loading
        
        loading += start
        loading += end
        loading.sort()
        
        for i in loading:print i
        
        
        end_index = 0
        if len(end) > len(start):
            for i in range(len(end) - len(start)):
                loading.remove(end[i])
        elif len(start) > len(end):
            for i in loading:
                if end_pattern.match(i):
                    end_index = loading.index(i)
        
        for i in range(end_index - 1):
            del loading[0]
        
        all = loading
        loading = []
        for i in all:
            loading.append(i)
            loading.append(all_lines.index(i))
        
        if not start_pattern.match(loading[0]):
            del loading[0]
        
        index = 0
        while index < len(loading):
            if len(loading) - index >= 4: 
                #print "start: "  +loading[index]
                start = loading[index].split(' ')
                index += 2
                end = loading[index].split(' ')
                #print "end: "+loading[index]
                gap = self.calculator(start[0] + ' ' + start[1], end[0]+ ' ' + end[1])
                index += 2
                loading.insert(index, gap)
            else:
                print 'loading in the end'
                break
            index += 1
        
        for i in loading: print i
        
        return loading

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
                self.error = 'ANR happened'
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
