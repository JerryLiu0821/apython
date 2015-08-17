# -*- coding: utf-8 -*-
'''
Created on Dec 31, 2013

@author: liujian
'''
import unittest
import sys
sys.path.append('../testcases')
import Stability,android
import os, time,datetime, re

class TestSourceLoading(unittest.TestCase):


    def setUp(self):
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.id = self.setup.device_id
        self.a.input.back(3)
        self.error=''
        self.source = {170:'Tuner', 4401:'VGA', 4402:'CVBS', 269:'HDMI'}
        for m in self.a.ui.windows():
            if "Application Error" in str(m):
                print m
                self.a.input.right()
                time.sleep(1)
                self.a.input.center()
                time.sleep(2)

    def tearDown(self):
        self.a.input.back(3)
        
    
    def testComponentLoadingTime(self):
        """分量信号加载的时间|按下分量信号到画面显示出来的时间"""
        try:
            self.a.device.sh('input keyevent 4401')
            time.sleep(10)
            self.a.device.sh('input keyevent 4404')
            time.sleep(1)
            self.a.input.up(3)
            self.a.input.down(3)
            self.a.input.center()
            time.sleep(20)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            
            #log_dir = "./liujian/report.20140616_163919/logs/00002/logcat_main.10.58.48.104:5555.1.txt"
            start_pattern = re.compile(r'.*LetvPinyinIME.*onKeyUp\ keyCode:23')
            #end_pattern = re.compile(r'.*MSrv_Picture::On\s+Skip.*AUTO_TEST\]\[source\ change\]:\ Unmute.*')
            end_pattern = re.compile(r'.*MSrv_Picture::On\s+Skip.*')
            loading = self.recode_analysis(log_dir, start_pattern, end_pattern)
            real = len(loading)/5 
            if real == 0:
                self.error = 'log error'
                raise Exception
            during = loading[(real-1)*5 + 4]
            print during
            self.a.log.debug("", "raise self.failureException('component loading time: %s ms')" %during)
            if 'no_signal' in self.a.ui.screen().ids():
                print 'no signal in component'
                self.error = 'no source in component'
            if during > 10000:
                self.error+"; loading time is lager then 10000ms"
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testTunerLoadingTime")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testTunerLoadingTime(self):
        """模拟电视加载的时间|按下模拟电视键到画面显示出来的时间"""
        try:
            self.a.device.sh("input keyevent 4401")
            time.sleep(10)
            self.a.device.sh("input keyevent 170")
            time.sleep(20)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            #log_dir = "./liujian/report.20140616_155330/logs/00001/logcat_main.10.58.48.104:5555.1.txt"
            start_pattern = re.compile(r'.*LetvPinyinIME.*onKeyUp\ keyCode:170')
            end_pattern = re.compile(r'.*SignalStable\ True')
            loading = self.recode_analysis(log_dir, start_pattern, end_pattern)
            real = len(loading)/5 
            if real == 0:
                self.error = 'log error'
                raise Exception
            loading_time = loading[(real-1)*5 + 4]
            self.a.log.debug("", "raise self.failureException('%s loading time: %s ms')" %(self.source[170],loading_time))
            if loading_time > 10000:
                self.error = 'time is lager then 10000ms'
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testTunerLoadingTime")
            self.fail("Error happened: %s %s" % (self.error, e))   
    
    def testVGALoadingTime(self):
        """电脑加载的时间|按下电脑键到画面显示出来的时间"""
        try:
            self.a.device.sh("input keyevent 170")
            time.sleep(10)
            self.a.device.sh("input keyevent 4401")
            time.sleep(20)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            #log_dir = "./liujian/report.20140616_162242/logs/00005/logcat_main.10.58.48.104:5555.1.txt"
            start_pattern = re.compile(r'.*LetvPinyinIME.*onKeyUp\ keyCode:4401')
            end_pattern = re.compile(r'.*MSrv_Picture::On\s+Skip.*AUTO_TEST\]\[source\ change\]:\ Unmute.*')
            end_pattern_e = re.compile(r'.*MSrv_Picture::On\s+Skip.*')
            loading = self.recode_analysis(log_dir, start_pattern, end_pattern)
            if loading == []:
                loading = self.recode_analysis(log_dir, start_pattern, end_pattern_e)
            real = len(loading)/5 
            if real == 0:
                self.error = 'log error'
                raise Exception
            loading_time = loading[(real-1)*5 + 4]
            self.a.log.debug("", "raise self.failureException('%s loading time: %s ms')" %(self.source[4401],loading_time))
            if loading_time > 10000:
                self.error = 'time is lager then 10000ms'
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testVGALoadingTime")
            self.fail("Error happened: %s %s" % (self.error, e)) 
    
    def testCVBSLoadingTime(self):
        """视频加载的时间|按下视频键到画面显示出来的时间"""
        try:
            self.a.device.sh("input keyevent 4401")
            time.sleep(10)
            self.a.device.sh("input keyevent 4402")
            time.sleep(20)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            #log_dir = "./liujian/report.20140616_155330/logs/00001/logcat_main.10.58.48.104:5555.1.txt"
            start_pattern = re.compile(r'.*LetvPinyinIME.*onKeyUp\ keyCode:4402')
            end_pattern = re.compile(r'.*MSrv_Picture::On\s+Skip.*')
            loading = self.recode_analysis(log_dir, start_pattern, end_pattern)
            real = len(loading)/5 
            if real == 0:
                self.error = 'log error'
                raise Exception
            loading_time = loading[(real-1)*5 + 4]
            self.a.log.debug("", "raise self.failureException('%s loading time: %s ms')" %(self.source[4402],loading_time))
            if loading_time > 10000:
                self.error = 'time is lager then 10000ms'
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testCVBSLoadingTime")
            self.fail("Error happened: %s %s" % (self.error, e)) 
    
    def testHDMILoadingTime(self):
        """HDMI加载的时间|按下HDMI键到画面显示出来的时间"""
        try:
            self.a.device.sh("input keyevent 4401")
            time.sleep(10)
            self.a.device.sh("input keyevent 269")
            time.sleep(20)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            
            #log_dir = "./liujian/report.20140617_100207/logs/00003/logcat_main.10.58.48.104:5555.1.txt"
            start_pattern = re.compile(r'.*LetvPinyinIME.*onKeyUp\ keyCode:269')
            end_pattern = re.compile(r'.*MSrv_Picture::On\s+Skip.*')
            loading = self.recode_analysis(log_dir, start_pattern, end_pattern)
            real = len(loading)/5 
            if real == 0:
                self.error = 'log error'
                raise Exception
            loading_time = loading[(real-1)*5 + 4]
            self.a.log.debug("", "raise self.failureException('%s loading time: %s ms')" %(self.source[269],loading_time))
            if loading_time > 10000:
                self.error = 'time is lager then 10000ms'
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testHDMILoadingTime")
            self.fail("Error happened: %s %s" % (self.error, e))
    
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
        
        if len(loading) == 2:
            if start_pattern.match(loading[1]):
                loading = []
        
        all = loading
        loading = []
        for i in all:
            loading.append(i)
            loading.append(all_lines.index(i))
            
        for i in loading: print i;
        
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
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
