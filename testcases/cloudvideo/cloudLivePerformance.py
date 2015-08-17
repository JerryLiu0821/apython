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

class TestPlayerPerformance(unittest.TestCase):


    def setUp(self):
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.stabdl = Stability.StabDL(self.a)
        self.error = ''
        self.id = self.setup.device_id 
        self.a.input.back(3)


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
        self.a.device.sh('input keyevent 4402')
        time.sleep(5)
        self.a.input.right()
        time.sleep(5)
        self.a.input.right()
        time.sleep(5)

    def testChangeOneChannel(self):
        """直播台1切到2的详细时间|"""
        try:
            self.navigateToLvie()
            self.a.device.sh("input keyevent 8")
            time.sleep(80)
            time.sleep(5)
            self.a.device.sh("input keyevent 166")
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            """
            log_dir = "../Log/Log_9205/liujian/report.20140903_171558/logs/00001/logcat_main.10.58.56.12:5555.1.txt"
            """
            self.handler(log_dir)
        except Exception, e:
            self.a.log.debug("", "\n testChangeLiveChannel")
            self.fail("Error happened: %s %s" % (self.error, e))

    def testChangeTwoChannel(self):
        """直播台2切到3的详细时间|"""
        try:
            self.navigateToLvie()
            self.a.device.sh("input keyevent 9")
            time.sleep(80)
            time.sleep(5)
            self.a.device.sh("input keyevent 166")
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            """
            log_dir = "./liujian/report.20140902_143033/logs/00001/logcat_main.10.58.49.172:5555.1.txt"
            """
            self.handler(log_dir)
        except Exception, e:
            self.a.log.debug("", "\n testChangeLiveChannel")
            self.fail("Error happened: %s %s" % (self.error, e))
    def testChangeThreeChannel(self):
        """直播台3切到4的详细时间|"""
        try:
            self.navigateToLvie()
            self.a.device.sh("input keyevent 10")
            time.sleep(80)
            time.sleep(5)
            self.a.device.sh("input keyevent 166")
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
#log_dir = "./liujian/report.20140808_110614/logs/00003/logcat_main.10.58.48.104:5555.1.txt"
            self.handler(log_dir)
        except Exception, e:
            self.a.log.debug("", "\n testChangeLiveChannel")
            self.fail("Error happened: %s %s" % (self.error, e))
    def testChangeFourChannel(self):
        """直播台4切到5的详细时间|"""
        try:
            self.navigateToLvie()
            self.a.device.sh("input keyevent 11")
            time.sleep(70)
            time.sleep(5)
            self.a.device.sh("input keyevent 166")
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            """
            log_dir = "../Log_Cloud_Daily/liujian/report.20140903_093157/logs/00005/logcat_main.10.58.48.104:5555.1.txt"
            """
            self.handler(log_dir)
        except Exception, e:
            self.a.log.debug("", "\n testChangeLiveChannel")
            self.fail("Error happened: %s %s" % (self.error, e))
    def testChangeFiveChannel(self):
        """直播台5切到6的详细时间|"""
        try:
            self.navigateToLvie()
            self.a.device.sh("input keyevent 12")
            time.sleep(80)
            time.sleep(5)
            self.a.device.sh("input keyevent 166")
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            """
            log_dir = "../Log_Cloud_Daily/liujian/report.20140903_093157/logs/00006/logcat_main.10.58.48.104:5555.1.txt"
            """
            self.handler(log_dir)
        except Exception, e:
            self.a.log.debug("", "\n testChangeLiveChannel")
            self.fail("Error happened: %s %s" % (self.error, e))
    def testChangeOneTo4k(self):
        """直播台1切换到4K频道的时间|"""
        try:
            self.navigateToLvie()
            time.sleep(15)
            self.a.device.sh("input keyevent 8")
            time.sleep(30)
            #press 30 channel
            self.a.device.sh("input keyevent 10")
            self.a.device.sh("input keyevent 7")
            time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            """
            log_dir = './liujian/report.20140901_144253/logs/00001/logcat_main.10.58.48.104:5555.1.txt'
            """
            cloud = Stability.cloudStatus(log_dir)
            result = cloud.playerProgress()
            during = -1
            for i in result: 
                if 'Time' in i:
                    during = i.split(':')[1].strip()
            self.a.log.debug("", "raise self.failureException('switch 1 to 4k time: %s ms')" %during)
            print "SHOW:",during
            if int(during) > 20000:
                self.error = "switch live 1 to 4k time is more than 20000ms"
                raise Exception

        except Exception, e:
            self.a.log.debug("", "\n testChangeLiveChannel")
            self.fail("Error happened: %s %s" % (self.error, e))

    def handler(self, log_dir):
        cloud = Stability.cloudStatus(log_dir)
        result = cloud.livePlayProgress()
        #self.a.log.debug("", "raise self.failureException('utp version: %s')" %(cloud.getUtpVersion()))
        output = [
        "频道切换的总时长",\
        "用户播放操作    应用获取播放地址",\
        "应用获取播放地址    播放器获取播放地址",\
        "播放器获取播放地址    播放器请求解析URL(M3U8)",\
        "播放器请求解析URL(M3U8)    UTP接收播放请求",\
        "UTP接收播放请求    UTP请求调度获取下载地址",\
        "UTP请求调度获取下载地址    UTP开始下载第一个m3u8",\
        "UTP开始下载第一个m3u8    UTP模块解析m3u8分配下载任务",\
        "UTP模块解析m3u8分配下载任务    UTP开始下载第一个分片",\
        "UTP开始下载第一个分片    UTP下载完成第一个分片",\
        "播放器请求解析URL(M3U8)    播放器获取并解析URL(M3U8)完成",\
        "播放器获取并解析URL(M3U8)完成    播放器请求第一个ts分段",\
        "播放器请求第一个ts分段    开始V/A初始化",\
        "开始V/A初始化    完成V/A初始化",\
        "完成V/A初始化    播放器Prepared",\
        "播放器Prepared    播放器start",\
        "播放器start    第一帧显示时间",\
        "utp获取镜像IP",\
        "UTP第一个分片(下载时长ms, 数据量Byte, 下载速度Bps)",\
        ]
        if len(result) != len(output):
            self.error = "cannot parser log"
            raise Exception
        during = re.search("\((\d+), '(.*)'\)", result[0]).group(2)
        print "SHOW:",during
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
                if re.compile('^\d+$').match(gap):
                    forp = int(gap)
                else:
                    forp = gap

            print output[i],":", forp 
            self.a.log.debug("", "raise self.failureException('%s:%s')" %(output[i],forp)) 
        if int(during) > 1800:
            self.error = "switch time %s ms more then 1800 ms" %during
            raise Exception
        elif isError:
            self.error = isError
            raise Exception

    def _testChangeLiveChannel(self):
        """直播台1切到6的详细时间|"""
        try:
            times = 5
            self.navigateToLvie()
            self.a.device.sh("input keyevent 8")
            time.sleep(20)
            time.sleep(5)
            for i in range(times):
                self.a.device.sh("input keyevent 166")
                time.sleep(30)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            cloud = Stability.cloudStatus(log_dir)
            result = cloud.playerProgress()
            user_press = r'.*Launcher.*:\ T2LauncherActivity\ --\ onKeyDown:\ KeyEvent\ \{\ action=ACTION_DOWN,\ keyCode=KEYCODE_CHANNEL_(UP|DOWN).*'
            fp = open(log_dir,"r+")
            fpp = open(os.path.join(android.log.report_directory(), android.log.logs_directory(),'logcat_main_liveswitch.txt'), "a+")
            first = 0
            logcat = fp.readlines()
            fp.close()
            for line in logcat:
                if re.compile(user_press).match(line):
                    first = logcat.index(line)
                    break
            fpp.writelines(logcat[first:])
            fpp.close()
            """
            log_dir = '../Log_Cloud_Daily/liujian/report.20140805_061127/logs/00002/logcat_main.10.58.48.104:5555.1.txt'
            cloud = Stability.cloudStatus(log_dir)
            result = cloud.playerProgress()
            """

            good = True
            total = []
            for i in result:
                if str(i).startswith("Time"):
                    print i
                    total.append(i)
            self.a.log.debug("", "raise self.failureException('直播频道1-6的切换时间为(ms): %s ')" %str(total) ) 
            i = 0
            while i < len(total):
                if int(total[i].split(":")[1]) > 2000:
                    good = False
                    self.error += "change %s to %s exceed time; "%(i+1,i+2)  
                    print "change %s to %s exceed time:"%(i+1,i+2),total[i]
                    self.a.log.debug("", "raise self.failureException('频道%s-%s超时: %s ms')" %(i+1, i+2,total[i]))
                    print 
                    if 'ERROR' not in str(result[result.index(total[i])+1]):
                        for j in range(1, 18):
                            print "details:", result[result.index(total[i])+j]
                            self.a.log.debug("", "raise self.failureException('详细时间为: %s ms')" %result[result.index(total[i])+j]) 
                    else:
                        print "details: ERROR"
                        self.a.log.debug("", "raise self.failureException('详细时间流程不正确 ')" ) 

                        
                i += 1 
            summ = 0
            for i in total:
                summ += int(i.split(":")[1])
            averg = summ/len(total)
            print "average time: %s" %averg
            self.a.log.debug("", "raise self.failureException('平均时间为: %s ms')" %averg) 
            if not good:
                raise Exception

                    
        except Exception, e:
            self.a.log.debug("", "\n testChangeLiveChannel")
            self.fail("Error happened: %s %s" % (self.error, e))  
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
