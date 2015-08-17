# -*- coding: utf-8 -*- 
'''
Created on Mar 10, 2014

@author: jerry
'''
import unittest
import android, Stability
import time, re, runtests,os,datetime
import random
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


class TestTunerBase(unittest.TestCase):

    def setUp(self):
        try:    
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.id = self.setup.device_id
            self.stabdl = Stability.StabDL(self.a)
            self.error = ''
            self.a.input.back(3)

        except Exception, e :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        pass
    
    def testSwitchBetweenATVAndDTMB(self):
        '''模拟电视 DTMB切换|在ATV和DTMB之间互相切换'''
        type = ''
        try:
            if not self.isAVSource():
                raise Exception
            for i in range(10):
                print 'loop %s' %i
                self.a.input.menu()
                for i in range(5):
                    if not self.isIdFocused('switch_source'):
                        self.a.input.up()
                    else:
                        break
                self.a.input.down()
                self.a.input.center()
                time.sleep(2)
                if self.isIdFocused('select_btn_dtv'):
                    self.a.input.left()
                    type = 'ATV'
                elif self.isIdFocused('select_btn_atv'):
                    self.a.input.right()
                    type = 'DTMB'
                else:
                    self.error = 'cannot open tuner source switch page'
                    raise Exception
                self.a.input.center()
                time.sleep(30)
                if not self.isOK(type):
                    raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testChannelUpByChannelKey")
            self.fail("Error happened: %s %s" % ( self.error, e))
        
    def testChangeATVScreenRate(self):
        """画面比例切换|切换ATV的画面"""
        try:
            if not self.isAVSource():
                raise Exception
            self.a.input.menu()
            for j in range(7):
                if not self.isIdFocused('setting_display_mode_switch'):
                    self.a.input.down()
                else:
                    break
            for i in range(15):
                self.a.input.center()
                time.sleep(20)
                if not self.isOK('ATV ScreenRate'):
                    raise Exception
                    
        except Exception, e:
            self.a.log.debug("", "\n testChangeATVScreenRate")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    def testChannelChangeByNumber(self):
        '''模拟电视数字切换频道|使用遥控器数字键调节频道'''
        try:
            if not self.isAVSource():
                raise Exception
            error_number = 0
            for i in range(2):
                which = random.randint(0,40)
                if which > 35:
                    which += 100
                if not self.pressChannelNumber(which):
                    error_number += 1
            if error_number > 0:
                print error_number
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testChannelUpByNumber")
            self.fail("Error happened: %s %s" % ( self.error, e))
        
    def testChangeChannelTime(self):
        """模拟电视切换频道时间|在模拟电视界面按频道加键到画面显示的时间"""
        try:
            times = 10
            if not self.isAVSource():
                raise Exception
            for i in range(times):
                self.a.device.sh("input keyevent 166")
                time.sleep(10)
            time.sleep(20)
            log_dir = os.path.join(android.log.report_directory(), android.log.logs_directory(), 'logcat_main.%s.1.txt' % self.id)
            
            #log_dir = './liujian/report.20140530_165216/logs/00001/logcat_main.10.58.48.104:5555.1.txt'
            
            start_pattern = re.compile(r'.*LetvPinyinIME.*onKeyDown\ keyCode:166')
            end_pattern = re.compile(r'.*SignalStable\ True.*')

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
                self.a.log.debug("", "raise self.failureException('模拟电视切换失败次数：%s')" % (times-real_times))
            self.a.log.debug("", "raise self.failureException('模拟电视切换%s次平均值: %s ms')" % (times,argv))
            if argv > 5000:
                self.error = 'change channel average time %s more then 5000 ms' %argv
                raise Exception
            
        except Exception, e:
            self.a.log.debug("", "\n testChangeChannelTime")
            self.fail("Error happened: %s %s" % ( self.error, e))
        
    def testChannelUpByChannelKey(self):
        '''模拟电视频道加|ATV界面按频道加键'''
        try:
            if not self.isAVSource():
                raise Exception
            error_number = 0
            for i in range(22):
                self.a.device.sh('input keyevent 166')
                number = self.getNumberAfterChannelChanged()
                if number == '':
                    error_number += 1
                else:
                    print 'now channel is: %s' %number
                if not self.isOK(number):
                    raise Exception
            
        except Exception, e:
            self.a.log.debug("", "\n testChannelUpByChannelKey")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    def testChannelDownByChannelKey(self):
        '''模拟电视频道减|ATV界面按频道减键'''
        try:
            if not self.isAVSource():
                raise Exception
            error_number = 0
            for i in range(22):
                self.a.device.sh('input keyevent 167')
                number = self.getNumberAfterChannelChanged()
                if number == '':
                    error_number += 1
                else:
                    print 'now channel is: %s' %number
                if not self.isOK(number):
                    raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testChannelDownByChannelKey")
            self.fail("Error happened: %s %s" % ( self.error, e))
    
    def pressChannelNumber(self, number):
        print 'press key %s' %number
        try:
            f = number / 10
            d = number % 10
            if f == 0:
                self.a.device.sh('input keyevent %s' %(d+7))
                time.sleep(3)
            elif f < 10:
                self.a.device.sh("input keyevent %s" %(f+7))
                self.a.device.sh("input keyevent %s" %(d+7))
                time.sleep(3)
            elif f < 100:
                m = f / 10
                md = f % 10
                self.a.device.sh("input keyevent %s" %(m+7))
                time.sleep(0.1)
                self.a.device.sh("input keyevent %s" %(md+7))
                time.sleep(0.1)
                self.a.device.sh("input keyevent %s" %(d+7))
                time.sleep(3)
            else:
                pass
            if not self.isOK("channel number %s" %number):
                return False
            else:
                return True

        except Exception, e:
            return False
    
    def isAVSource(self):
        try:
            self.a.device.sh('input keyevent 170')
            time.sleep(1)
            w = self.a.ui.screen()
            if 'port_info_content3' in w.ids():
                return True 
            else:
                ###############################################
                ###### need to add scan channel
                ###############################################
                return True
                
        except :
            return False
    
    def getNumberAfterChannelChanged(self):
        try:
            channelNumber = self.a.ui.waitfor(id='channel_number').text().encode('utf-8')
            return channelNumber
        except :
            return ''
    
    def isIdExist(self,id):
        try:
            self.a.waitfor(id=id)
            return True
        except:
            return False
        
    
    def isIdFocused(self,idname):
        try:
            self.a.ui.waitfor(id=idname,isFocused=True)
            return True
        except:
            return False
    
    def launchTV(self):
        self.a.device.sh("input keyevent 170")
        time.sleep(15)
        if 'com.letv.signalsourcemanager/com.letv.signalsourcemanager.MainActivity' not in self.a.ui.window():
            self.error = 'cannot launch signal sourcemanager'
            raise Exception
    
    def isOK(self,type):
        time.sleep(5)
        try:
            widgets = self.a.ui.waitfor(
                anyof=[
                    self.a.ui.widgetspec(id='message'),
                    self.a.ui.widgetspec(id='progressBar'),
                    self.a.ui.widgetspec(id='no_signal'),])
            wid = widgets.id()
            if wid == 'message':
                self.a.input.down()
                self.a.input.center()
                self.error = "Force Closed after press %s" %type
                return False
            if wid == 'progressBar':
                self.error = 'loading ... after press %s ' %type
                return False
            if wid == 'no_signal':
                self.error = 'no signal after press %s ' %type
                return False
            else:
                self.a.log.debug("", "No Force Closed & ANR happen!")
                return True
            
        except:
            return True


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
        
        all = loading
        loading = []
        for i in all:
            loading.append(i)
            loading.append(all_lines.index(i))
        
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
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
