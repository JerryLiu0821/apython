# -*- coding: utf-8 -*-
'''
Created on Dec 19, 2013

@author: liujian
'''
import unittest, time, os, re, datetime
import android, runtests
import sys
sys.path.append('../testcases')
reload(sys)
sys.setdefaultencoding('utf8')
import Stability

class TestPlayerPerformance(unittest.TestCase):


    def setUp(self):
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.stabdl = Stability.StabDL(self.a)
        self.error = ''
        self.id = self.setup.device_id 
        self.a.input.back(3)
        for m in self.a.ui.windows():
            if "Application Error" in str(m):
                print m
                self.a.input.right()
                time.sleep(1)
                self.a.input.center()
                time.sleep(2)

    def tearDown(self):
        self.a.input.back(3)
    
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
    
    def navigateToLvie(self):
        self.a.device.sh('input keyevent 4401')
        time.sleep(5)
        self.a.input.right()
        time.sleep(5)
        self.a.input.right()
        time.sleep(5)
      
    def launchTestFileManager(self):
        cmd = 'am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -f 0x10200000 -n com.letv.filemanager/.FileExplorerTabActivity'
        self.a.device.sh(cmd)
        time.sleep(5)
    
    def operateDesktopStyle(self,position, opt):
        self.a.device.sh("input keyevent 176")
        time.sleep(2)
        self.a.input.left(8)
        self.a.input.down()
        self.a.input.right()
        self.a.input.center()
        time.sleep(2)
        self.a.input.up(4)
        #\u901a\u7528\u7248 通用版  
        #\u6781\u901f\u7248 极速版
        #\u5f00\u542f 开启  
        #\u5173\u95ed 关闭
        #\u8f6e\u64ad\u9891\u9053 轮播频道
        #\u4fe1\u53f7\u8f93\u5165 信号源输入
        self.a.input.down(position -1 )
        default = ''
        if position == 1 or position == 3:
            default = u'\u5f00\u542f'
        elif position == 2:
            default = u'\u8f6e\u64ad\u9891\u9053'
        elif position == 4:
            default = u'\u901a\u7528\u7248'
           
        w = self.a.ui.screen()
        if opt == 'open':
            if default not in w.texts()[position*2-1]:
                print 'open'
                self.a.input.center()
                time.sleep(1)
        elif opt == 'close':
            if default in w.texts()[position*2-1]:
                print 'close'
                self.a.input.center()
                time.sleep(1)
        else:
            self.error = ' input error '
            print 'input error'
            raise Exception
        self.a.input.back(3)
        
    def testRebootPlayerStartTime(self):
        """开机起播时间|开机以后进入到直播界面，直播的起播时间"""
        try:
            self.operateDesktopStyle(2, 'open')
            time.sleep(2)
            self.a.device.sh("su -c reboot reboot")
            print 'sleep 30'
            time.sleep(30)
            os.system('adb disconnect' + self.id)
            time.sleep(1)
            os.system('adb connect %s' %self.id)
            time.sleep(1)
            os.system('adb -s %s root' %self.id)
            time.sleep(1)
            os.system('adb connect %s' %self.id)
            time.sleep(1)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory())
            print 'pull log'
            os.system('adb -s %s pull /data/Logs/Log.0/logcat.log %s' %(self.id, log_dir))
            during = self.playerPrepareTime(os.path.join(log_dir, 'logcat.log'))
            self.a.log.debug("", "raise self.failureException('刚开机的起播时间: %s ms')" %during )
            if during > 1500:
                self.error = 'player start time %s is more then 1500ms after reboot tv' %during
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testSourceToLiveLoadingTime")
            self.fail("Error happened: %s %s" % (self.error, e))
        
    def testTunerToLiveLoadingTime(self):
        """Tuner信号切换到直播台时间|从Tuner信号切换到直播台，直播台的detect时间"""
        try:
            self.a.device.sh("input keyevent 4401")
            time.sleep(10)
            self.operateDesktopStyle(4, 'close')
            self.a.device.sh("input keyevent 170")
            time.sleep(5)
            if 'select_btn_atv' in self.a.ui.screen().ids():
                self.a.input.left()
                self.a.input.center()
                time.sleep(2)
                self.a.input.back(4)
                time.sleep(2)
                time.sleep(10)
            time.sleep(10)
            self.a.input.right()
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            
            #log_dir = './liujian/report.20140528_110014/logs/00001/logcat_main.192.168.1.100:5555.1.txt'
            start_pattern = re.compile(r'.*LetvPinyinIME.*onKeyDown\ keyCode:22')
            end_pattern = re.compile(r'.*MediaPlayerService.*:\ \[\d+\] start\ done')
            during_list = self.recode_analysis(log_dir,start_pattern,  end_pattern)
            
            for i in during_list: print i
            real_times = len(during_list)/5
            during = during_list[real_times*5 -1]
            self.a.log.debug("", "raise self.failureException('Tuner to live time: %s ms')" %during)
            print during
            if during > 3000:
                self.error = 'Tuner to live time %s is more then 3000ms' %during
                raise Exception
            self.operateDesktopStyle(4, 'open')
            
        except Exception,e:
            self.operateDesktopStyle(4, 'open')
            self.a.log.debug("", "\n testSourceToLiveLoadingTime")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testCVBSToLiveLoadingTime(self):
        """CVBS信号切换到直播台时间|从Tuner信号切换到直播台，直播台的detect时间"""
        try:
            self.operateDesktopStyle(4, 'close')
            self.a.device.sh("input keyevent 4402")
            time.sleep(20)
            self.a.input.right()
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            
            #log_dir = './liujian/report.20140528_110014/logs/00001/logcat_main.192.168.1.100:5555.1.txt'
            start_pattern = re.compile(r'.*LetvPinyinIME.*onKeyDown\ keyCode:22')
            end_pattern = re.compile(r'.*MediaPlayerService.*:\ \[\d+\] start\ done')
            during_list = self.recode_analysis(log_dir,start_pattern,  end_pattern)
            
            for i in during_list: print i
            real_times = len(during_list)/5
            during = during_list[real_times*5 -1]
            self.a.log.debug("", "raise self.failureException('CVBS to live time: %s ms')" %during)
            print during
            if during > 3000:
                self.error = 'CVBS to live time %s is more then 3000ms' %during
                raise Exception
            self.operateDesktopStyle(4, 'open')
            
        except Exception,e:
            self.operateDesktopStyle(4, 'open')
            self.a.log.debug("", "\n testCVBSToLiveLoadingTime")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testVGAToLiveLoadingTime(self):
        """VGA信号切换到直播台时间|从Tuner信号切换到直播台，直播台的detect时间"""
        try:
            self.operateDesktopStyle(4, 'close')
            self.a.device.sh("input keyevent 4401")
            time.sleep(20)
            self.a.input.right()
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            
            #log_dir = './liujian/report.20140528_110014/logs/00001/logcat_main.192.168.1.100:5555.1.txt'
            start_pattern = re.compile(r'.*LetvPinyinIME.*onKeyDown\ keyCode:22')
            end_pattern = re.compile(r'.*MediaPlayerService.*:\ \[\d+\] start\ done')
            during_list = self.recode_analysis(log_dir,start_pattern,  end_pattern)
            
            for i in during_list: print i
            real_times = len(during_list)/5
            during = during_list[real_times*5 -1]
            self.a.log.debug("", "raise self.failureException('VGA to live time: %s ms')" %during)
            print during
            if during > 3000:
                self.error = 'VGA to live time %s is more then 3000ms' %during
                raise Exception
            self.operateDesktopStyle(4, 'open')
            
        except Exception,e:
            self.operateDesktopStyle(4, 'open')
            self.a.log.debug("", "\n testVGAToLiveLoadingTime")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testHDMIToLiveLoadingTime(self):
        """HDMI信号切换到直播台时间|从Tuner信号切换到直播台，直播台的detect时间"""
        try:
            self.operateDesktopStyle(4, 'close')
            self.a.device.sh("input keyevent 269")
            time.sleep(20)
            self.a.input.right()
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            
            #log_dir = './liujian/report.20140528_110014/logs/00001/logcat_main.192.168.1.100:5555.1.txt'
            start_pattern = re.compile(r'.*LetvPinyinIME.*onKeyDown\ keyCode:22')
            end_pattern = re.compile(r'.*MediaPlayerService.*:\ \[\d+\] start\ done')
            during_list = self.recode_analysis(log_dir,start_pattern,  end_pattern)
            
            for i in during_list: print i
            real_times = len(during_list)/5
            during = during_list[real_times*5 -1]
            self.a.log.debug("", "raise self.failureException('HDMI to live time: %s ms')" %during)
            print during
            if during > 3000:
                self.error = 'HDMI to live time %s is more then 3000ms' %during
                raise Exception
            self.operateDesktopStyle(4, 'open')
            
        except Exception,e:
            self.operateDesktopStyle(4, 'open')
            self.a.log.debug("", "\n testHDMIToLiveLoadingTime")
            self.fail("Error happened: %s %s" % (self.error, e))
               
    def testChangeLiveChannel(self):
        """直播频道切换时间|按遥控器键到画面显示的时间"""
        try:
            times = 5
            start_pattern = re.compile(r'.*LetvPinyinIME.*onKeyDown\ keyCode:166')
            end_pattern = re.compile(r'.*MediaPlayerService.*:\ \[\d+\] start\ done')

            self.navigateToLvie()
            time.sleep(5)
            for i in range(5):
                self.a.device.sh("input keyevent 166")
                time.sleep(20)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            
            #log_dir = './liujian/report.20140528_123106/logs/00001/logcat_main.192.168.1.100:5555.1.txt'
            during_list = self.recode_analysis(log_dir,start_pattern,  end_pattern)
            
            real_times = len(during_list)/5
            if real_times == 0:
                self.error = 'change channel failed'
                raise Exception
            argv = -1
            sum = 0
            for i in range(1,real_times+1):
                print 'change channel %s: %s' %(i,during_list[i*5-1])
                self.a.log.debug("", "raise self.failureException('change channel %s: %s ms')" %(i,during_list[i*5-1]))
                sum += during_list[i*5-1]
            argv = sum/real_times
            print 'average time is: %s' %argv
            if real_times != times:
                self.a.log.debug("", "raise self.failureException('直播台切换失败次数：%s')" % (times-real_times))
            self.a.log.debug("", "raise self.failureException('直播台切换%s次平均值: %s ms')" % (times,argv))
            if argv > 2000:
                self.error = 'change channel average time %s is more then 2000ms' %argv
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testChangeLiveChannel")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def _testVideoPrepareToFirstFrame(self):
        """视频解码器初始化到播放第一祯|视频解码器初始化到播放第一祯的时间"""
        try:
            self.url = "http://10.204.8.236:8080/vod/a.m3u8"
            """码流：1Mkbs；分辨率：1024*576；祯率：25fps"""
            cmd = "am start -a android.intent.action.VIEW -d \'%s\' -n com.letv.videoplayer/.MainActivity" % self.url
            self.a.device.sh(cmd)
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            print log_dir
            during = self.videotoFirstFrame(log_dir)
            self.a.log.debug("", "raise self.failureException('视频解码器初始化到播放第一祯的时间: %s ms')" % during)
            if during == -1:
                raise Exception
            elif during > 1200:
                self.error = 'video decode init to first frame display time %s ms  is more then 1200ms' % during
                raise Exception
        
        except Exception, e :
            self.a.log.debug("", "\n testVideoPrepareToFirstFrame")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testLivePlayPrepareTime(self):
        """直播起播时间|切换直播台查看直播台起播的时间 """
        try:
            self.navigateToLvie()
            time.sleep(2)
            self.a.device.sh('input keyevent KEYCODE_6')
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            during = self.playerPrepareTime(log_dir)
            print during
            self.a.log.debug("", "raise self.failureException('直播播放器实例化到播放器准备完毕的时间: %s ms')" % during)
            if during == -1:
                raise Exception
            if during > 1200:
                self.error = 'live player prepare time more then 1200ms'
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testLivePlayPrepareTime")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testLivePlayerCloseTime(self):
        """直播播放器关闭的时间|切换直播台，查看直播播放器关闭的时间"""
        try:
            self.navigateToLvie()
            time.sleep(2)
            self.a.input.channel_up()
            time.sleep(5)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            during = self.playerCloseTime(log_dir)
            print during
            self.a.log.debug("", "raise self.failureException('直播播放器关闭的时间: %s ms')" % during)
            if during == -1:
                raise Exception
            if during > 800:
                self.error = 'live player close time more then 800ms'
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testLivePlayerCloseTime")
            self.fail("Error happened: %s %s" % (self.error, e))
        
    def testVodPlayPrepareTime(self):
        """点播起播时间|日志中筛选出setDataSource到prepare的时间"""
        try:
            self.url = "http://10.204.8.236:8080/vod/a.m3u8"
            """码流：1Mkbs；分辨率：1024*576；祯率：25fps"""
            self.launchTestFileManager()
            cmd = "am start -a android.intent.action.VIEW -d \'%s\' -n com.letv.videoplayer/.MainActivity" % self.url
            self.a.device.sh(cmd)
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            print log_dir
            
            during = self.playerPrepareTime(log_dir)
            if during > 1200:
                self.error = 'spend %s ms > 1200ms' % during
                raise Exception
            elif during == -1:
                raise Exception
            self.a.log.debug("", "raise self.failureException('点播播放器实例化到播放器准备完毕的时间: %s ms')" % during)
        
        except Exception, e :
            self.a.log.debug("", "\n testVodPlayPrepareTime")
            self.fail("Error happened: %s %s" % (self.error, e))
        
    def testVodPlayerCloseTime(self):
        """点播播放器关闭时间|点播播放器关闭的时间 """
        try:
            self.url = "http://10.204.8.236:8080/vod/a.m3u8"
            cmd = "am start -a android.intent.action.VIEW -d \'%s\' -n com.letv.videoplayer/.MainActivity" % self.url
            self.launchTestFileManager()
            self.a.device.sh(cmd)
            time.sleep(15)
            self.a.input.back()
            time.sleep(5)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            print log_dir
            during = self.playerCloseTime(log_dir)
            self.a.log.debug("", "raise self.failureException('点播播放器关闭的时间: %s ms')" % during)
            if during == -1:
                raise Exception
            if during > 800 :
                self.error = 'close vod player time more then 800ms '
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testVodPlayerCloseTime")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testVodUserCloseTime(self):
        """点击退出到播放器关闭时间|用户点击退出到播放器关闭的时间 """
        try:
            self.url = "http://10.204.8.236:8080/vod/a.m3u8"
            cmd = "am start -a android.intent.action.VIEW -d \'%s\' -n com.letv.videoplayer/.MainActivity" % self.url
            self.launchTestFileManager()
            self.a.device.sh(cmd)
            time.sleep(15)
            self.a.input.back()
            time.sleep(5)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            print log_dir
            during = self.userCloseTime(log_dir)
            self.a.log.debug("", "raise self.failureException('点播播放器关闭的时间: %s ms')" % during)
            if during == -1:
                raise Exception
            if during > 800 :
                self.error = 'close vod player time more then 800ms '
                raise Exception
        except Exception, e :
            self.a.log.debug("", "\n testVodPlayerCloseTime")
            self.fail("Error happened: %s %s" % (self.error, e))
        
    def testVodPlayerSeekTime(self):
        """Vod seek时间 | 播放点播视频并快进，查看seek时间"""
        try:
            self.url = "http://10.204.8.236:8080/vod/a.m3u8"
            cmd = "am start -a android.intent.action.VIEW -d \'%s\' -n com.letv.videoplayer/.MainActivity" % self.url
            self.launchTestFileManager()
            self.a.device.sh(cmd)
            time.sleep(15)
            self.a.input.right(2)
            time.sleep(5)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            print log_dir
            during = self.seekTime(log_dir)
            self.a.log.debug("", "raise self.failureException('点播播放器seek的时间: %s ms')" % during)
            if during == -1:
                raise Exception
            if during > 600 :
                self.error = 'seek vod player time more then 600ms '
                raise Exception
            #self.a.log.debug("", "raise self.failureException('点播播放器seek的时间: %s ms')" % during)
        except Exception, e :
            self.a.log.debug("", "\n testVodPlayerSeekTime")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def testPlayerLoading(self):
        """播放视频中出现loading次数和loading时间|日志中查看loading次数和每次loading的时间"""
        try:
            #http://192.168.1.101/webdav/discontinuity.m3u8
            self.launchTestFileManager()
            self.url = "http://10.204.8.236:8080/vod/a.m3u8"
            cmd = "am start -a android.intent.action.VIEW -d \'%s\' -n com.letv.videoplayer/.MainActivity" % self.url
            self.a.device.sh(cmd)
            print 'playing 1800s'
            time.sleep(180)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            print log_dir
            
            #log_dir = './liujian/report.20140527_102448/logs/00004/logcat_main.192.168.1.100:5555.1.txt'
            
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
        except Exception, e :
            print Exception.message
            self.a.log.debug("", "\n testPlayerLoading")
            self.fail("Error happened: %s %s" % (self.error, e))
    
    def changeChannelTime(self,logdir):
        get_list_start = ''
        get_list_end = ''
        #D/LetvPinyinIME( 3713): record_sound -- onKeyDown keyCode:4
        pattern_start = re.compile(r'.*LetvPinyinIME.*onKeyDown\ keyCode:166')
        fp = open(logdir, 'r')
        all_lines = fp.readlines()
        fp.close()
            
        for line in all_lines:
            match_start = pattern_start.match(line)
            if match_start:
                get_list_start = match_start.group()
            pattern_end = re.compile(r'.*MediaPlayerService.*:\ \[\d+\] start\ done')
            match_end = pattern_end.match(line)
            if match_end:
                get_list_end = match_end.group()
            
        if get_list_start == '' or get_list_end == '':
            self.error = 'seek failed'
            return -1
        print get_list_start
        print get_list_end
        
        during = self.calculator(get_list_start[:18], get_list_end[:18])
        
        print during
        return during
    
    def videotoFirstFrame(self,logdir):
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
            
        _start_time = get_list_start.split()[1][6:]
        _end_time = get_list_end.split()[1][6:]
        start_time = _start_time.split('.')
        end_time = _end_time.split('.')
        during = (int(end_time[0]) * 1000 + int(end_time[1])) - (int(start_time[0]) * 1000 + int(start_time[1]))
        print during
        return during
    
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
        
    def playerCloseTime(self, logdir):
        """ param: log file directory
            func: if player close fine then return ms for player close time else return -1
            """
        get_list_start = ''
        get_list_end = ''
        #MediaPlayerService: [40] stop done
        pattern_start = re.compile(r'.*MediaPlayerService:\ \[(\d+)\]\ stop\ done')
        fp = open(logdir, 'r')
        all_lines = fp.readlines()
        fp.close()
            
        pipeline = 1
        for line in all_lines:
            match_start = pattern_start.match(line)
            if match_start:
                pipeline = match_start.group(1)
                get_list_start = match_start.group()
            #MediaPlayerService: [40] disconnect done
            pattern_end = re.compile(r'.*MediaPlayerService:\ \[%s\]\ disconnect\ done' % pipeline)
            match_end = pattern_end.match(line)
            if match_end:
                get_list_end = match_end.group()
            
        if get_list_start == '' or get_list_end == '':
            self.error = 'cannot close player'
            return -1
        print get_list_start
        print get_list_end
        
        during = self.calculator(get_list_start[:18], get_list_end[:18])
        
        print during
        return during
    
    def seekTime(self, logdir):
        """ param: log file directory
            func: if seek fine then return ms for player close time else return -1
            """
        get_list_start = ''
        get_list_end = ''
        #D/LetvPinyinIME( 3713): record_sound -- onKeyDown keyCode:4
        pattern_start = re.compile(r'.*LetvPinyinIME.*onKeyDown\ keyCode:22')
        fp = open(logdir, 'r')
        all_lines = fp.readlines()
        fp.close()
            
        for line in all_lines:
            match_start = pattern_start.match(line)
            if match_start:
                get_list_start = match_start.group()
            #01-07 01:15:01.656 V/MediaPlayerService( 2402): [26] notify (0x43f6e960, 4, 0, 0)
            #pattern_end = re.compile(r'.*MediaPlayerService.*\ notify\ \(\w+,\ 4,\ 0,\ 0\)')
            pattern_end = re.compile(r'.*MediaPlayerService.*:\ \[\d+\] start\ done')
            match_end = pattern_end.match(line)
            if match_end:
                get_list_end = match_end.group()
            
        if get_list_start == '' or get_list_end == '':
            self.error = 'seek failed'
            return -1
        print get_list_start
        print get_list_end
        
        during = self.calculator(get_list_start[:18], get_list_end[:18])
        
        print during
        return during
        
    #目前截图看不到图片的内容，无法实现
    
    def userCloseTime(self, logdir):
        """ param: log file directory
            func: if player close fine then return ms for player close time else return -1
            """
        get_list_start = ''
        get_list_end = ''
        #D/LetvPinyinIME( 3713): record_sound -- onKeyDown keyCode:4
        pattern_start = re.compile(r'.*LetvPinyinIME.*onKeyDown\ keyCode:4')
        fp = open(logdir, 'r')
        all_lines = fp.readlines()
        fp.close()
            
        for line in all_lines:
            match_start = pattern_start.match(line)
            if match_start:
                get_list_start = match_start.group()
            #01-06 21:49:11.990 V/MediaPlayerService( 2399): disconnect(8) end
            pattern_end = re.compile(r'.*MediaPlayerService:.*disconnect\(\d+\)\ .*')
            match_end = pattern_end.match(line)
            if match_end:
                get_list_end = match_end.group()
            
        if get_list_start == '' or get_list_end == '':
            self.error = 'cannot close player'
            return -1
        print get_list_start
        print get_list_end
        
        during = self.calculator(get_list_start[:18], get_list_end[:18])
        
        print during
        return during
    
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

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
