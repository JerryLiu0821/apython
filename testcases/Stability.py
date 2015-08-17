import android, time, unittest, sys, datetime, copy,os,re


import re
import os
import traceback
import commands


from threading import Thread #To check heap usage



LOOP_IDLE = 10  #Seconds

MADGPENNYTOSS_INSTALLED = 0
MADGCHICKEN_INSTALLED = 0
MADGHORSE_INSTALLED = 0

MENU_DELAY = 10

SERIAL_INTERFACE = None


def doc(f):
    def checkdoc(s):
        doc = getattr(f, '__doc__')
        if doc is None:
            setattr(f, '__doc__', "None|")
        elif '|' not in doc:
            doc = doc + "|"
            setattr(f, '__doc__', doc)
        else:pass
        return f
    return checkdoc



class takeMeminfo():
    def __init__(self, id, meminfo_dir):
        self.id = id
        self.meminfo_dir = meminfo_dir
        self.procrank = "procrank.log"
        self.dumsys = "dumpsys_meminfo.log"
        self.top = "top.log"

    def meminfo(self):
        if not os.path.isdir(self.meminfo_dir):
            print self.meminfo_dir + "is not a directory"
            return

        fp = open(os.path.join(self.meminfo_dir,self.procrank), "a+")
        fd = open(os.path.join(self.meminfo_dir,self.dumsys), "a+")
        ft = open(os.path.join(self.meminfo_dir,self.top), "a+")
        try:
            fp.write(commands.getoutput("adb -s %s shell procrank" %self.id))
            fp.write("\n================================\n")
            fd.write(commands.getoutput("adb -s %s shell dumpsys meminfo" %self.id))
            fp.write("\n================================\n")
            ft.write(commands.getoutput("adb -s %s shell busybox top -n 1" %self.id))
            fp.write("\n================================\n")
            fp.close()
            fd.close()
            ft.close()

        except:
            fp.close()
            fd.close()
            ft.close()
            raise Exception

class UiAutomator():
    """run UiAutomator case"""
    def __init__(self,id, jarname, casename, argname="none", argvalue="none"):
        self.id = id
        self.jar = jarname
        self.case = casename
        self.arg = argname
        self.argvalue = argvalue

    def runtest(self):
        """return result and info list

            eg.
            ua = Stability.UiAutomator(self.id, self.jar, self.case)
            result, info = ua.runtest()
            if result != 'PASS':
                print str(info)
                raise Exception
        """
        pushcmd = "adb -s %s push ../testcases/setup/%s /data/local/tmp" %(self.id, self.jar)
        cmd = "adb -s %s shell uiautomator runtest %s --nohup -c %s -e %s %s" %(self.id,self.jar, self.case, self.arg, self.argvalue)
        push = commands.getstatusoutput(pushcmd)
        if push[0] != 0:
            return '',[push[1]]
        output = commands.getstatusoutput(cmd)
        uilog = []
        if output[0]==0:
            for line in output[1].split('\r\n'):
                l = line.strip()
                if l:
                    uilog.append(l)
        else:
            return '', [output[1]] 
        result = ''
        for i in range(len(uilog)):
            if uilog[i].startswith("Time:"):
                if uilog[i+1].startswith("OK"):
                    result = 'PASS'
                else:
                    result = 'FAIL'
        info = []
        for line in uilog:
            print line
            if line.startswith('Result'):
                info.append(line.split(':', 1)[1])
            if line.startswith('INSTRUMENTATION_STATUS: stack='):
                info.append(line)
            if line.startswith("INSTRUMENTATION_STATUS: fail file"):
                info.append(line)
            if line.endswith('KB/s'):
                info.append(line)
            if line.endswith('MB/s'):
                info.append(line)
        return result, info

class cloudStatus():
    """detect cloud video status"""
    def __init__(self, filename):
        self.filename = filename

    def playerError(self):
        """return MediaPlayer Error times"""
        logcontents = self.openFile()
        p = re.compile(r'MediaPlayer: error')
        result = 0
        if logcontents != []:
            for line in logcontents:
                if p.search(line):
                    result += 1
        else:
            print self.filename + " is null"
        print "MediaPlayer: error:  %s" %result
        return result

    def getUtpVersion(self):
        """return utp version"""
        logcontents = self.openFile()
        p = re.compile(r'\[UTPModule\]\ utp\ status:\ (.*)\ .*')
        duration = -1
        if logcontents !=[]:
            for line in logcontents:
                match = p.search(line)
                if match:
                    duration = match.group(1)
        return duration

    def getPlayDuration(self):
        """return play duration"""
        logcontents = self.openFile()
        p = re.compile(r'MediaPlayerService.*: \[\d+\] getDuration = (\d+)')
        duration = -1
        if logcontents !=[]:
            for line in logcontents:
                match = p.search(line)
                if match:
                    duration = match.group(1)
        print "duration: %s" %duration
        return duration

    def getResolution(self):
        """return resolution"""
        logcontents = self.openFile()
#MediaPlayerService( 1232): [42] notify (0x40076db0, 5, 640, 352)
#MediaPlayerService: [33] notify (0x4e4fbe30, 5, 1280, 720)
#MediaPlayerService: [27] notify (0x539209a0, 5, 1280, 720)
        p = re.compile(r'.*MediaPlayerService.*:\ \[\d+\]\ notify\ \(\w+,\ 5,\ (\d+),\ (\d+)\)\s*')
        resolution = ""
        if logcontents !=[]:
            for line in logcontents:
                match = p.match(line)
                if match:
                    resolution = match.group(1)+"*"+match.group(2)
                    break
        print "Resolution: %s" %resolution
        return resolution

    def checkVodStopStatus(self):
        """return exit player correct or wrong"""
        isExit = False
        logcontents = self.openFile()
        allstatus = []
        stop = r'.*MediaPlayerService.*: \[(\d+)\] stop\s*$'
        stop_done = r'.*MediaPlayerService.*: \[\d+\] stop done\s*$'
        disconnect = r'.*MediaPlayerService.*: disconnect\(\d+\) from pid \d+\s*$'
        disconnect_done= r'.*MediaPlayerService.*: \[\d+\] disconnect done\s*$'
        if logcontents != []:
            for i in range(len(logcontents)):
                if re.compile("|".join([stop,stop_done,disconnect,disconnect_done])).match(logcontents[i]):
                    allstatus.append(str(i)+" "+logcontents[i])

        if allstatus != []:
            allstatus.sort()
            #for i in allstatus:print i
        else:
            print "stop progress is null"
            return isExit
        i=0
        while (i < len(allstatus)):
            if re.compile(stop).match(allstatus[i]):
                flag = 1
                pipe = re.compile(stop).match(allstatus[i]).group(1)
                for j in range(i+1,len(allstatus)):
                    if re.compile(r'.*MediaPlayerService.*: \[%s\] stop done\s*$' %pipe).match(allstatus[j]):
                        flag += 1
                        i = j+1
                        for k in range(j+1, len(allstatus)):
                            if re.compile(r'.*MediaPlayerService.*: disconnect\(%s\) from pid \d+\s*$' %pipe).match(allstatus[k]):
                                flag += 1
                                i=k+1
                                for m in range(k+1, len(allstatus)):
                                     if re.compile(r'.*MediaPlayerService.*: \[%s\] disconnect done\s+$' %pipe).match(allstatus[m]):
                                         flag += 1
                                         i = k+1
                                         break
                                break
                        break
                    else:
                        i += 1
                if flag != 4:
                    print "exit player error %s" %pipe
                    isExit = False
                else:
                    isExit = True
                    print "exit corrected %s" %pipe

            else:
                i += 1

        return isExit

    def checkVodPlayStatus(self):
        """return playing is incremental or not"""
        incremental = True
        logcontents = self.openFile()
        positions = []
        p = re.compile(r'.*MediaPlayerService.*: \[\d+\] getCurrentPosition = (\d+)\s+$')
        if logcontents != []:
            for line in logcontents:
                match = p.match(line)
                if match:
                    positions.append(int(match.group(1)))

        org = copy.copy(positions)
        positions.sort()
        return org == positions

    def checkVodPauseStatus(self):
        """return if player is paused or not"""
        logcontents = self.openFile()
        pause = []
        pause_pattern = r'.*VideoPlayer-VideoPlayer.*: onKeyUp keyCode = 23'
        if logcontents != []:
            for i in logcontents:
                if re.compile(pause_pattern).match(i):
                    pause.append(i)
        else:
            print 'logcat is null'
            return False
        if len(pause) == 0:
            print 'not pause'
            return False

        times = len(pause)/2
        print 'pause times: %s' %times
        flag = 0
        if times == 0:
            for j in range(logcontents.index(pause[i-1]), len(logcontents)):
                if re.compile(r'.*MediaPlayerService.*: \[\d+\] getCurrentPosition =\d+$').match(j):
                    flag += 1
                    break
        else:
             for i in range(times):
                 for j in range(logcontents.index(pause[i*2]), logcontents.index(pause[i*2+1])):
                     if re.compile(r'.*MediaPlayerService.*: \[\d+\] getCurrentPosition =\d+$').match(logcontents[j]):
                         flag += 1
                         print 'pause failed'
                         break
        if flag != 0:
            print "player cannot pause"
            return False
        else:
             return True

    def checkVodHlsSeekStatus(self):
        """return seek status"""
        logcontents = self.openFile()
        seek = []
        pseek = r'.*MediaPlayerService.*: \[(\d+)\] seekTo\((\d+)\)\s*$'
        seek_done = r'.*MediaPlayerService.*: \[\d+\] seekTo done\s*$'
        seek_notify = r'.*MediaPlayerService.*: \[\d+\] notify \(\w+, 4, 0, 0\)\s*$'
        position = r'.*MediaPlayerService.*: \[\d+\] getCurrentPosition = (\d+)\s*$'
        if logcontents != []:
            for i in range(len(logcontents)):
                if re.compile("|".join([pseek,seek_done,seek_notify,position])).match(logcontents[i]):
                    seek.append(str(i)+" "+logcontents[i])
        if seek == []:
            print "no seek in %s" %self.filename
        seek.sort()
        ok = True
        i=0
        while(i < len(seek)):
            matchi = re.compile(pseek).match(seek[i])
            if matchi:
                pipe = matchi.group(1)
                seekto = matchi.group(2)
                flag = False
                for j in range(i+1,len(seek)):
                    matchj = re.compile(r'.*MediaPlayerService.*: \[%s\] getCurrentPosition = (\d+)\s*$' %pipe).match(seek[j])
                    if matchj:
                        cposition = matchj.group(1)
                        i = j+1
                        flag = True
                        kd = int(seekto) - int(cposition)
# if the src is hls the kd is 25000, if http the kd is 10000
                        if kd > 25000 or kd < -25000:
                            print "seekTo(%s), getCurrentPosition = %s" %(seekto,cposition)
                            ok = False;
                        break
                if not flag:
                    print "no getCurrentPosition found after seekTo(%s)" %seekto
                    i = len(seek)
            else:
                i += 1
        return ok

    def checkVodHttpSeekStatus(self):
        """return seek status"""
        logcontents = self.openFile()
        seek = []
        pseek = r'.*MediaPlayerService.*: \[(\d+)\] seekTo\((\d+)\)\s*$'
        seek_done = r'.*MediaPlayerService.*: \[\d+\] seekTo done\s*$'
        seek_notify = r'.*MediaPlayerService.*: \[\d+\] notify \(\w+, 4, 0, 0\)\s*$'
        position = r'.*MediaPlayerService.*: \[\d+\] getCurrentPosition = (\d+)\s*$'
        if logcontents != []:
            for i in range(len(logcontents)):
                if re.compile("|".join([pseek,seek_done,seek_notify,position])).match(logcontents[i]):
                    seek.append(str(i)+" "+logcontents[i])
        if seek == []:
            print "no seek in %s" %self.filename
        seek.sort()
        ok = True
        i=0
        while(i < len(seek)):
            matchi = re.compile(pseek).match(seek[i])
            if matchi:
                pipe = matchi.group(1)
                seekto = matchi.group(2)
                flag = False
                for j in range(i+1,len(seek)):
                    matchj = re.compile(r'.*MediaPlayerService.*: \[%s\] getCurrentPosition = (\d+)\s*$' %pipe).match(seek[j])
                    if matchj:
                        cposition = matchj.group(1)
                        i = j+1
                        flag = True
                        kd = int(seekto) - int(cposition)
# if the src is hls the kd is 25000, if http the kd is 10000
                        if kd > 10000 or kd < -10000:
                            print "seekTo(%s), getCurrentPosition = %s" %(seekto,cposition)
                            ok = False;
                        break
                if not flag:
                    print "no getCurrentPosition found after seekTo(%s)" %seekto
                    i = len(seek)
            else:
                i += 1
        return ok

    def livePlayProgress(self):
        """return a progress list """
        def list_during(re_s, re_e, l):
            """return flag, gap 
                flag:0: not match any line;1: match start; 2: match end; 3: match start and end"""
            r=[]
            flag = 0
            if l != []:
                for i in l:
                    if re.compile(re_s).match(i):
                        r.append(i)
                        flag += 1 
                        break
                for i in l:
                    if re.compile(re_e).match(i):
                        r.append(i)
                        flag += 2
                        break
            if flag == 3:
                return flag,  str(self.calculatorbak(r[0][:18],r[1][:18]))
            return flag,'error' 
        user_press = r'.*Launcher.*:\ T2LauncherActivity\ --\ onKeyDown:\ KeyEvent\ \{\ action=ACTION_DOWN,\ keyCode=KEYCODE_CHANNEL_(UP|DOWN).*'
        launcher_get_url = r'.*Launcher.*:\ LivePlayerController\ --\ play\(\)\ -\ uri:(\S+)\ pip:\ false\s*$'
        player_get_url = r'.*MediaPlayerService.*:\ \[(\d+)\]\ setDataSource\((\S+)\)'
#player_prepare = r'.*MediaPlayerService.*:\ \[(\d+)\]\ prepareAsync\s*$'
        player_post_m3u8 = r'.*DataSource_M3U8.*:\ \[parseURLs\]\ try\ parseURLs=(\S+)'
        utp_get_first_request = r'.*\[utp_play_handler\]\ handle_request\ 127\.0\.0\.1:\d+\ \ /play?.*'
        utp_request_download_url = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ http://live\.gslb\.letv\.com/gslb.*'
        utp_download_first_m3u8 = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ http://.*/desc\.m3u8\?.*'
        utp_parser_m3u8_assign_download_task = r'.*\[app\]\ add\ slice.*'
        utp_start_download_first_slice = r'.*\[downloader\]\ start_download\ http_range:bytes=0-\d+\ (.*)'
        utp_finish_download_first_slice = r'.*\[downloader\]\ on_http_complete.*'
        player_finish_parser_m3u8 = r'.*\[init\]\ parseURLs\ Success!\ urlNum\ :\ 3'
        player_post_first_ts_slice = r'.*\[init\]\ \[M3u8\]\ post\ cmd\ for\ start\ first\ url:(\S+)'
        init_video = r'.*Creating\ Video\ Decoder\ video/avc'
        init_video_end = r'.*Video\ Decoder\ instantiante\ end'
        init_audio = r'.*Creating\ Audio\ Decoder\ audio.*'
        init_audio_end = r'.*Audio\ Decoder\ instantiante\ end'
        player_prepared =r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 1,\ 0,\ 0\)'
        player_start = r'.*MediaPlayerService.*:\ \[(\d+)\]\ start\s*$'
        first_frame = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 3,\ 0\)'

        utp_handle_mirrors = r'.*\[xml_content_parser\]\ handle_mirrors\ http.*'


        regex = [user_press,launcher_get_url,player_get_url,player_post_m3u8,utp_request_download_url,player_finish_parser_m3u8, init_video,init_video_end,init_audio,init_audio_end,player_prepared,player_start,first_frame]
        regex_first = [utp_download_first_m3u8, utp_parser_m3u8_assign_download_task, utp_start_download_first_slice, player_post_first_ts_slice, utp_handle_mirrors]
#regex_first remove utp_get_first_request
#regex_first remove utp_finish_download_first_slice to match url from utp_start_download_first_slice
        len_regex_first = len(regex_first) + 2

        rr = "|".join(regex)

        progress = []
        logcontents = self.openFile()
        index = 0
        last = index
        setDataSourceIndex = 0
        if logcontents != []:
            for line in logcontents:
                if re.compile(user_press).match(line):
                    index = logcontents.index(line)
                    break
            for line in logcontents[index:]:
                if re.compile(first_frame).match(line):
                    last = logcontents.index(line) + 1
                    break
            for line in logcontents[index:]:
                if re.compile(player_get_url).match(line):
                    setDataSourceIndex = logcontents.index(line)
                    break
        else:
            return
        for line in logcontents[index:last]:
            if re.compile(rr).match(line):
                progress.append(line)

        first_request = 0
        for line in logcontents[setDataSourceIndex:last]:
            if re.compile(utp_get_first_request).match(line):
                progress.append(line)
                first_request = logcontents.index(line)
                break
        for line in logcontents[first_request:last]:
            for i in regex_first:
                if re.compile(i).match(line):
                    progress.append(line)
                    regex_first.remove(i)
                    break

        #utp_finish_download_first_slice to match url from utp_start_download_first_slice
        for line in logcontents[first_request:last]:
            match = re.compile(utp_start_download_first_slice).match(line)
            if match:
                url = match.group(1)
                i = logcontents.index(line)
                for l in logcontents[i:]:
                    if url in l and "on_http_complete" in l:
                        progress.append(l)
                        break
                break
        progress.sort()
        print "progress:",len(progress)
        for i in progress: print i
        result = []
        if len(progress) != (len(regex) + len_regex_first):
            print 'length is not matched'
#return result

        # init V/A 
        av = []
        for i in progress:
            if re.compile("|".join([init_video,init_video_end,init_audio,init_audio_end])).match(i):
                av.append(i)
        av.sort()
        for i in av: print i

        progress.remove(av[1])
        progress.remove(av[2])
        # end init V/A
        for i in progress: print i
        
        result.append("user_press -> first_frame: " + str(list_during(user_press,first_frame,progress)))
        result.append("user_press -> launcher_get_url: " + str(list_during(user_press,launcher_get_url,progress)))
        result.append("launcher_get_url -> player_get_url: " + str(list_during(launcher_get_url,player_get_url,progress)))
        result.append("player_get_url -> player_post_m3u8: " + str(list_during(player_get_url,player_post_m3u8,progress)))
#result.append("player_get_url -> player_prepare: " + str(list_during(player_get_url,player_prepare,progress)))
#result.append("player_prepare -> player_post_m3u8: " + str(list_during(player_prepare,player_post_m3u8,progress)))
        result.append("player_post_m3u8 -> utp_get_first_request: " + str(list_during(player_post_m3u8,utp_get_first_request,progress)))
        result.append("utp_get_first_request -> utp_request_download_url: " + str(list_during(utp_get_first_request,utp_request_download_url,progress)))
        result.append("utp_request_download_url -> utp_download_first_m3u8: " + str(list_during(utp_request_download_url,utp_download_first_m3u8,progress)))
        result.append("utp_download_first_m3u8 -> utp_parser_m3u8_assign_download_task: " + str(list_during(utp_download_first_m3u8,utp_parser_m3u8_assign_download_task,progress)))
        result.append("utp_parser_m3u8_assign_download_task -> utp_start_download_first_slice: " + str(list_during(utp_download_first_m3u8,utp_start_download_first_slice,progress)))
        result.append("utp_start_download_first_slice -> utp_finish_download_first_slice: " + str(list_during(utp_start_download_first_slice,utp_finish_download_first_slice,progress)))
        result.append("player_post_m3u8 -> player_finish_parser_m3u8: " + str(list_during(player_post_m3u8,player_finish_parser_m3u8,progress)))
        result.append("player_finish_parser_m3u8 -> player_post_first_ts_slice: " + str(list_during(player_finish_parser_m3u8,player_post_first_ts_slice,progress)))
        result.append("player_post_first_ts_slice -> init_video/audio: " + str(list_during(player_post_first_ts_slice,"|".join([init_video,init_audio]),progress)))
        result.append("init_video/audio -> init_audio/video_end: " + str(list_during("|".join([init_video,init_audio]),"|".join([init_audio_end,init_video_end]),progress)))
        result.append("init_audio/video_end -> player_prepared: " + str(list_during("|".join([init_audio_end,init_video_end]),player_prepared,progress)))
        result.append("player_prepared -> player_start: " + str(list_during(player_prepared,player_start,progress)))
        result.append("player_start -> first_frame: " + str(list_during(player_start,first_frame,progress)))
        for i in progress:
            if re.compile(utp_handle_mirrors).match(i):
                result.append("utp_handle_mirrors: " + str((3, re.search('\[xml_content_parser\]\ handle_mirrors http://[\d\.]+', i).group())))
            if re.compile(utp_finish_download_first_slice).match(i):
                result.append("utp_finish_download_first_slice_data: " + str((3, re.search('\[downloader\] on_http_complete \(\(\d+,\d+\),\d+\) \(\d+,\d+,\d+\)', i).group())))
        if "utp_finish_download_first_slice_data:" not in str(result):
            result.append("utp_finish_download_first_slice_data: " + str((0, 'error')))


        for i in result: print i

        return result

    def vodHttpPlayProgress(self):
        """return vod play progress"""
        def list_during(re_s, re_e, l):
            """return flag, gap 
                flag:0: not match any line;1: match start; 2: match end; 3: match start and end"""
            r=[]
            flag = 0
            if l != []:
                for i in l:
                    if re.compile(re_s).match(i):
                        r.append(i)
                        flag += 1 
                        break
                for i in l:
                    if re.compile(re_e).match(i):
                        r.append(i)
                        flag += 2
                        break
            if flag == 3:
                return flag,  str(self.calculatorbak(r[0][:18],r[1][:18]))
            return flag,'error' 

        #
        user_press = r'.*LETVPlay:\ jumpToPlay\s*$'
        tvban_get_url = r'.*LinkShellUtil:\ getURLFromLink\ outPut:(.*$)'
        player_get_url = r'.*MediaPlayerService.*:\ \[(\d+)\]\ setDataSource\((\S+)\)'
        player_request_download = r'.*HTTPStreamCurl:\ \[HTTPStreamCurl\]\ HTTPStreamCurl Connecting to :.*'
        utp_get_first_request = r'.*\[utp_play_handler\] handle_request 127\.0\.0\.1:\d+ bytes=0- /play\?.*'
        utp_request_download_url = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ http://g3\.letv\.cn/vod.*'
        utp_download_first_data = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ .*'
        utp_start_download_first_slice = r'.*\[downloader\]\ start_download\ http_range:bytes=0-\d+ (.*)'
        utp_finish_download_first_slice = r'.*\[downloader\]\ on_http_complete.*'
        #player_request_success = r'.*StreamContentSource::connect OK !!'
        init_video = r'.*Creating\ Video\ Decoder\ video/avc'
        init_video_end = r'.*Video\ Decoder\ instantiante\ end'
        init_audio = r'.*Creating\ Audio\ Decoder\ audio.*'
        init_audio_end = r'.*Audio\ Decoder\ instantiante\ end'
        player_prepared =r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 1,\ 0,\ 0\)'
        player_start = r'.*MediaPlayerService.*:\ \[(\d+)\]\ start\s*$'
        first_frame = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 3,\ 0\)'

        #after user_press
        regex = [user_press,tvban_get_url,player_get_url,player_request_download,init_video,init_video_end,init_audio,init_audio_end,player_prepared,player_start,first_frame]
        #after utp_get_first_request
        #utp_finish_download_first_slice url must match utp_start_download_first_slice
        regex_first = [utp_get_first_request,utp_request_download_url,utp_download_first_data, utp_start_download_first_slice]

        rr = "|".join(regex)

        progress = []
        logcontents = self.openFile()
        if logcontents == []:
            print 'logcat is null'
            return []

        #find user press
        index = 0
        for line in logcontents:
            if re.compile(user_press).match(line):
                index = logcontents.index(line)
                break

        for line in logcontents[index:]:
            if re.compile(rr).match(line):
                progress.append(line)

        #only one utp_get_first_request after user press
        utp_index = 0
        for line in logcontents[index:]:
            if re.compile(utp_get_first_request).match(line):
                utp_index = logcontents.index(line)
                break

        for line in logcontents[utp_index:]:
            for i in regex_first:
                if re.compile(i).match(line):
                    progress.append(line)
                    regex_first.remove(i)
                    break

        #utp_finish_download_first_slice to match url from utp_start_download_first_slice
        for line in logcontents[utp_index:]:
            match = re.compile(utp_start_download_first_slice).match(line)
            if match:
                url = match.group(1)
                i = logcontents.index(line)
                for l in logcontents[i:]:
                    if url in l and "on_http_complete" in l:
                        progress.append(l)
                        break
                break
        progress.sort()
        print "progress:",len(progress)
        #for i in progress: print i
        result = []

        # init V/A 
        av = []
        for i in progress:
            if re.compile("|".join([init_video,init_video_end,init_audio,init_audio_end])).match(i):
                av.append(i)
        av.sort()

        progress.remove(av[1])
        progress.remove(av[2])
        # end init V/A
        for i in progress: print i
        
        result.append("user_press -> first_frame: " + str(list_during(user_press,first_frame,progress)))
        result.append("user_press -> tvban_get_url: " + str(list_during(user_press,tvban_get_url,progress)))
        result.append("tvban_get_url -> player_get_url: " + str(list_during(tvban_get_url,player_get_url,progress)))
        result.append("player_request_download -> utp_get_first_request: " + str(list_during(player_request_download,utp_get_first_request,progress)))
        result.append("utp_get_first_request -> utp_request_download_url: " + str(list_during(utp_get_first_request,utp_request_download_url,progress)))
        result.append("utp_request_download_url: -> utp_download_first_data: " + str(list_during(utp_request_download_url, utp_download_first_data,progress)))
        result.append("utp_start_download_first_slice -> utp_finish_download_first_slice: " + str(list_during(utp_start_download_first_slice,utp_finish_download_first_slice,progress)))
        result.append("utp_get_first_request -> init_video/audio: " + str(list_during(utp_get_first_request,"|".join([init_video,init_audio]),progress)))
        result.append("init_video/audio -> init_audio/video_end: " + str(list_during("|".join([init_video,init_audio]),"|".join([init_audio_end,init_video_end]),progress)))
        result.append("init_audio/video_end -> player_prepared: " + str(list_during("|".join([init_audio_end,init_video_end]),player_prepared,progress)))
        result.append("player_prepared -> player_start: " + str(list_during(player_prepared,player_start,progress)))
        result.append("player_start -> first_frame: " + str(list_during(player_start,first_frame, progress)))

        for i in result: print i

        return result

    def vodHlsPlayProgress(self):
        """return vod play progress"""
        def list_during(re_s, re_e, l):
            """return flag, gap 
                flag:0: not match any line;1: match start; 2: match end; 3: match start and end"""
            r=[]
            flag = 0
            if l != []:
                for i in l:
                    if re.compile(re_s).match(i):
                        r.append(i)
                        flag += 1 
                        break
                for i in l:
                    if re.compile(re_e).match(i):
                        r.append(i)
                        flag += 2
                        break
            if flag == 3:
                return flag,  str(self.calculatorbak(r[0][:18],r[1][:18]))
            return flag,'error' 

        #
        key_down = r'.*injectKeyEvent:\ KeyEvent\ \{\ action=ACTION_DOWN,\ keyCode=KEYCODE_DPAD_CENTER.*'
        user_press = r'.*LETVPlay:\ jumpToPlay\s*$'
        tvban_get_url = r'.*LinkShellUtil:\ getURLFromLink\ outPut:(.*$)'
        player_get_url = r'.*MediaPlayerService.*:\ \[(\d+)\]\ setDataSource\((\S+)\)'
        player_post_m3u8 = r'.*DataSource_M3U8.*:\ \[parseURLs\]\ try\ parseURLs=(\S+)'
        utp_get_first_request = r'.*\[utp_play_handler\]\ handle_request\ 127\.0\.0\.1:\d+\ \ /play?.*'
        utp_request_download_url = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ http://g3\.letv\.cn/vod.*'
        utp_download_first_m3u8 = r'.*\[downloader\]\ start_download\ http_range:bytes=-\ http://.*/.*\.m3u8\?.*'
        utp_start_download_first_slice = r'.*\[downloader\]\ start_download\ http_range:bytes=0-\d+ (.*)'
        utp_finish_download_first_slice = r'.*\[downloader\]\ on_http_complete.*'
        player_finish_parser_m3u8 = r'.*\[init\]\ parseURLs\ Success!\ urlNum\ :\ 3'
        player_post_first_ts_slice = r'.*\[init\]\ \[M3u8\]\ post\ cmd\ for\ start\ first\ url:(\S+)'
        init_video = r'.*Creating\ Video\ Decoder\ video/avc'
        init_video_end = r'.*Video\ Decoder\ instantiante\ end'
        init_audio = r'.*Creating\ Audio\ Decoder\ audio.*'
        init_audio_end = r'.*Audio\ Decoder\ instantiante\ end'
        player_prepared =r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 1,\ 0,\ 0\)'
        player_start = r'.*MediaPlayerService.*:\ \[(\d+)\]\ start\s*$'
        first_frame = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 3,\ 0\)'


        #after user_press
        regex = [user_press,tvban_get_url,player_get_url,player_post_m3u8,init_video,init_video_end,init_audio,init_audio_end,player_prepared,player_start,first_frame]
        #after utp_get_first_request
        #utp_finish_download_first_slice url must match utp_start_download_first_slice
        regex_first = [utp_get_first_request,utp_request_download_url, utp_download_first_m3u8, utp_start_download_first_slice, player_finish_parser_m3u8, player_post_first_ts_slice]

        rr = "|".join(regex)

        progress = []
        logcontents = self.openFile()
        if logcontents == []:
            print 'logcat is null'
            return []

        #find user press
        index = 0
        for line in logcontents:
            if re.compile(user_press).match(line):
                index = logcontents.index(line)
                break

        for line in logcontents[index:]:
            if re.compile(rr).match(line):
                progress.append(line)

        #only one utp_get_first_request after user press
        utp_index = 0
        for line in logcontents[index:]:
            if re.compile(utp_get_first_request).match(line):
                utp_index = logcontents.index(line)
                break

        for line in logcontents[utp_index:]:
            for i in regex_first:
                if re.compile(i).match(line):
                    progress.append(line)
                    regex_first.remove(i)
                    break

        #utp_finish_download_first_slice to match url from utp_start_download_first_slice
        for line in logcontents[utp_index:]:
            match = re.compile(utp_start_download_first_slice).match(line)
            if match:
                url = match.group(1)
                i = logcontents.index(line)
                for l in logcontents[i:]:
                    if url in l and "on_http_complete" in l:
                        progress.append(l)
                        break
                break
        progress.sort()
        print "progress:",len(progress)
        #for i in progress: print i
        result = []

        # init V/A 
        av = []
        for i in progress:
            if re.compile("|".join([init_video,init_video_end,init_audio,init_audio_end])).match(i):
                av.append(i)
        av.sort()

        progress.remove(av[1])
        progress.remove(av[2])
        # end init V/A
        for i in progress: print i
        
        result.append("user_press -> first_frame: " + str(list_during(user_press,first_frame,progress)))
        result.append("user_press -> tvban_get_url: " + str(list_during(user_press,tvban_get_url,progress)))
        result.append("tvban_get_url -> player_get_url: " + str(list_during(tvban_get_url,player_get_url,progress)))
        result.append("player_get_url -> player_post_m3u8: " + str(list_during(player_get_url,player_post_m3u8,progress)))
#result.append("player_get_url -> player_prepare: " + str(list_during(player_get_url,player_prepare,progress)))
#result.append("player_prepare -> player_post_m3u8: " + str(list_during(player_prepare,player_post_m3u8,progress)))
        result.append("player_post_m3u8 -> utp_get_first_request: " + str(list_during(player_post_m3u8,utp_get_first_request,progress)))
        result.append("utp_get_first_request -> utp_request_download_url: " + str(list_during(utp_get_first_request,utp_request_download_url,progress)))
        result.append("utp_request_download_url -> utp_download_first_m3u8: " + str(list_during(utp_request_download_url,utp_download_first_m3u8,progress)))
        result.append("utp_download_first_m3u8 -> utp_start_download_first_slice: " + str(list_during(utp_download_first_m3u8,utp_start_download_first_slice,progress)))
        result.append("utp_start_download_first_slice -> utp_finish_download_first_slice: " + str(list_during(utp_start_download_first_slice,utp_finish_download_first_slice,progress)))
        result.append("player_post_m3u8 -> player_finish_parser_m3u8: " + str(list_during(player_post_m3u8,player_finish_parser_m3u8,progress)))
        result.append("player_finish_parser_m3u8 -> player_post_first_ts_slice: " + str(list_during(player_finish_parser_m3u8,player_post_first_ts_slice,progress)))
        result.append("player_post_first_ts_slice -> init_video/audio: " + str(list_during(player_post_first_ts_slice,"|".join([init_video,init_audio]),progress)))
        result.append("init_video/audio -> init_audio/video_end: " + str(list_during("|".join([init_video,init_audio]),"|".join([init_audio_end,init_video_end]),progress)))
        result.append("init_audio/video_end -> player_prepared: " + str(list_during("|".join([init_audio_end,init_video_end]),player_prepared,progress)))
        result.append("player_prepared -> player_start: " + str(list_during(player_prepared,player_start,progress)))
        result.append("player_start -> first_frame: " + str(list_during(player_start,first_frame,progress)))

        for i in result: print i

        return result


    def playerProgress(self):
        """return a list includes switch time and each progress time """
        user_press = r'.*Launcher.*:\ T2LauncherActivity\ --\ onKeyDown:\ KeyEvent\ \{\ action=ACTION_DOWN,\ keyCode=KEYCODE_0.*'
        launcher_get_url = r'.*Launcher.*:\ LivePlayerController\ --\ play\(\)\ -\ uri:(\S+)\ pip:\ false\s*$'
        player_get_url = r'.*MediaPlayerService.*:\ \[(\d+)\]\ setDataSource\((\S+)\)'
        player_get_app_init_time = r'.*MediaPlayerService.*:\s+request-time\ :\ (\d+)\s*$'
        player_prepare = r'.*MediaPlayerService.*:\ \[(\d+)\]\ prepareAsync\s*$'
        post_m3u8 = r'.*DataSource_M3U8.*:\ \[M3U8\]\ try\ parseURLs=(\S+)'
        get_first_m3u8 = r'.*DataSource_M3U8.*:\s+mHttpResponseCode\ =\ 200\s*$'
        post_first_ts_slice = r'.*DataSource_M3U8.*:\ \[M3U8\]----->post\ cmd\ for\ start\ first\ url:(\S+),\ knowedFileSize:0'
        player_prepared =r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 1,\ 0,\ 0\)'
        player_start = r'.*MediaPlayerService.*:\ \[(\d+)\]\ start\s*$'
        player_start_done = r'.*MediaPlayerService.*:\ \[(\d+)\]\ start\ done\s*$'
        first_frame = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 3,\ 0\)'
        start_loading = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 701,\ 0\)\s*$'
        end_loading = r'.*MediaPlayerService.*:\ \[(\d+)\]\ notify\ \(\w+,\ 200,\ 702,\ 0\)\s*$'
        player_stop = r'.*MediaPlayerService.*:\ \[(\d+)\]\ stop\s*$'
        player_stop_done = r'.*MediaPlayerService.*:\ \[(\d+)\]\ stop\ done\s*$'
        player_release = r'.*MediaPlayerService.*: disconnect\((\d+)\)\ from\ pid\ \d+\s*$'
        player_release_done    = r'.*MediaPlayerService.*:\ \[(\d+)\]\ disconnect\ done\s*$'

        regex = [user_press,launcher_get_url,player_get_url, player_get_app_init_time, player_prepare, post_m3u8,get_first_m3u8, post_first_ts_slice,\
         player_prepared, player_start,player_start_done, first_frame, start_loading, end_loading, player_stop,player_stop_done,  player_release, player_release_done]
        rr = "|".join(regex)

        progress = []
        logcontents = self.openFile()
        index = 0
        last = 0
        if logcontents != []:
            for line in logcontents:
                if re.compile(user_press).match(line):
                    index = logcontents.index(line)
                    last = index
                    break
            for line in logcontents[index:]:
                if re.compile(first_frame).match(line):
                    last = logcontents.index(line)+1
                    break
        else:
            return
        for line in logcontents[index:last]:
            if re.compile(rr).match(line):
                progress.append(line)

        during = []
        result = []
        for line in progress:
            #print line
            if re.compile("|".join([user_press, first_frame])).match(line):
                during.append(line)
        if len(during)%2 !=0 or len(during)==0:
            print "not start in the end"
        else:
            i=0
            while i < len(during):
                countTime = self.calculatorbak(during[i][:18], during[i+1][:18])
                result.append("Time:"+str(countTime))
                onep = progress[progress.index(during[i]):progress.index(during[i+1])+1]
                onesp = []
                if len(onep) != len(regex):
                    for rep in regex:
                        for each in onep:
                            if re.compile(rep).match(each):
                                onesp.append(each)
                                break
                    onesp.sort()
                else:
                    onesp = onep
                #print exceed time line 
                if countTime > 2000:
                    for ll in onesp: print ll
                #while the output log grogress is right
                if len(onesp) == len(regex):
                    j=0
                    while j < len(onesp)-1:
                        result.append(self.calculatorbak(onesp[j][:18], onesp[j+1][:18]))
                        j += 1
                    #while the output log is more then range
                else:
                    result.append("ERROR")
                    print "ERROR"

                i += 2
        return result

    def openFile(self):
        fp = open(self.filename, "r+")
        contents=[]
        try:
            contents = fp.readlines();
            fp.close()
        except Exception, e:
            fp.close()
            print e
        return contents

    def calculatorbak(self, start_str, end_str):
        """
        params: time format like 12-19 17:31:34.166
        return: int mseconds
        """
        def timeToMS(stri):
            stri_a = stri.split(' ')[0]
            stri_b = stri.split(" ")[1]
            M = int(stri_a.split("-")[0].strip())
            d = int(stri_a.split("-")[1].strip())
            h = int(stri_b.split(":")[0])
            m = int(stri_b.split(":")[1])
            s = int(stri_b.split(":")[2].split(".")[0])
            ms = int(stri_b.split(".")[1])
            return ms+s*1000+m*60*1000+h*60*60*1000+d*24*60*60*1000
        return timeToMS(end_str) - timeToMS(start_str)


    def calculator(self, start_str, end_str):
        """
        params: time format like 12-19 17:31:34.166
        return: int mseconds
        """
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
        return int(s*1000+ms*1000)        


class PlayFiles():
            
    def __init__(self, a, playtime):
        self.a = a
        self.play_urls=[]
        self.error_urls = []
        self.start_over = 1
        self.i =0
        self.outloop = 1
        self.playtime = playtime
    def getPlayFiles(self, Media_Type):
        
        media_str = self.a.device.sh('busybox find /storage/external_storage/sda1/QA-Streams -name *.' + Media_Type)
        #media_str = self.a.device.sh('busybox find /mnt/usb/ -name *.' + Media_Type)

        #media_str += self.a.device.sh('find /storage -name *.' + Media_Type)
        media_list = media_str.split('\r\n') 
        l = len(media_list)
        for i in range(0, l-1):
            self.play_urls.append(media_list[i]) #Add all local videos to list web_urls. 
         
    def ifImagePlayOrCompleted(self, displayID):
        try:
            self.a.input.down()
            self.a.input.center()
            time.sleep(5)
            w = self.a.ui.waitfor( anyof = [                
                self.a.ui.widgetspec(id='player_error_iv'),
                self.a.ui.widgetspec(id=displayID),
                self.a.ui.widgetspec( text='Cannot play video'),
                self.a.ui.widgetspec( id='alertTitle'),
                self.a.ui.widgetspec(id='video'),
                self.a.ui.widgetspec(id='app_home'),
                self.a.ui.widgetspec(text='Wait'),
                self.a.ui.widgetspec(id='message', text=re.compile(r'(^Unfortunately.*stopped\.$)')) 
                 ])
            w_text=w.text()
            w_id = w.id()
            if w_id==displayID :
                self.a.input.right(5)
                time.sleep(1)
                self.a.input.left(3)
                time.sleep(1)
                self.a.input.center(2)
                time.sleep(1)
                return True     
            elif w_id=='player_error_iv' :
                self.a.input.back(2)
                return False
            elif  w_id=='app_home' :
                return False
            
            elif w_id=='alertTitle':
                self.a.input.right()
                self.a.input.center()
                w=self.a.ui.screen()
                time.sleep(1)
                if "alertTitle" in str(w.ids()):
                    self.a.input.right()
                    self.a.input.center()
                return False
    
            elif w_text=='Wait':
                self.a.input.down()
                self.a.input.right() #Choose resumeplaying button
                self.a.input.center()
                self.error_urls.append('ANR happened while playing ')
                self.error_urls.append(self.play_urls[self.i])
                raise Exception
            elif w_id=='message':
                self.a.input.down()
                self.a.input.center()
                self.error_urls.append('force close happened while playing ')
                self.error_urls.append(self.play_urls[self.i])
                raise Exception
            elif w_id=='video':
                return False

            self.a.log.debug("","This image is playing successfully.")

            #time.sleep(self.playtime)
            return True
        except Exception, e:
            raise Exception     
        
    def playFiles(self, Media_Type, component, type, displayID):
        self.getPlayFiles(Media_Type)
        self.loop=len(self.play_urls)   
        #w=self.a.ui.screen() #Switch to app screen and the live play is not in the background.
        '''for i in range (0,4):
            if 'app_name' not in w.ids():
                self.a.input.home()
                w.refresh()
            elif 'video' in w.ids():
                self.a.device.sh("input keyevent 176")
                time.sleep(2)
                self.a.input.up()
                self.a.input.right(3)
                self.a.input.center(2)
                self.a.input.back(2)                
                break
            else:
                break'''
             
        for j in range(1, self.outloop+1):
            for self.i in range (0,self.loop):
                cmd = "am start -a android.intent.action.VIEW -n %s  -t \'%s/*\' -d \'file://%s\'"%(component, type, self.play_urls[self.i].strip('\r'))
                #cmd = "am start -n letv.lcworld.player/.MainActivity -d \'%s\' -a android.intent.action.VIEW"%self.play_urls[i]
                self.a.device.sh(cmd)

                if self.ifImagePlayOrCompleted(displayID): # Playing right
                    print "Pass: playing %s "%(self.play_urls[self.i])
                    self.a.log.debug("","This image: %s is played successfully."%self.play_urls[self.i])
                    self.a.input.back()
                    
                else:  # Playing error
                    print "Fail: playing %s."%(self.play_urls[self.i])
                    self.error_urls.append(self.play_urls[self.i])
                    self.a.log.debug("","Error: %s This image can not be played."%self.play_urls[self.i])                   
                
                time.sleep(2)
                             
            self.a.input.back(2)
            time.sleep(5)
        #if self.error_urls!=[]:
            #raise Exception


class MonitorMemoryUsage(Thread): #For any applications, threads etc... which have a process id.
    def __init__(self,test_dev,process_name,initial_monitor_value,trigger_value, monitor_duration):
        self.test_dev = test_dev
        self.process_name = str(process_name)
        self.device_id = android.settings.DEVICES['TestDevice']['id']
        '''try:
            cmd1 = os.popen ('adb devices')
            self.device_ids = cmd1.readlines()[1:-1]
            if (len(self.device_ids)==1 and 'device' in str(self.device_ids) ):
                self.device_id = self.device_ids[0].split('\t')[0]
            cmd1.close()raise Exception
        except:
            print 'Failed to get adb devices.\n' '''
        
        self.log_directory = str(self.device_id)+'_Heap_Logs'
        self.dumpsys_output = None
        self._stop_thread = False #Since we are using a single thread, we will use a single variable to stop this thread
        self.monitor_duration = monitor_duration
        self.first_watch_trigger = False

        if initial_monitor_value is not None:
            self.initial_monitor_value = initial_monitor_value

        if trigger_value is not None:
            self.trigger_value = trigger_value

        try:
            os.mkdir(self.log_directory)
        except Exception, e:
            if '[Errno 17]' in str(e):
                print ''
                print 'Directory '+str(self.log_directory)+' already exists...'
                print ''

        self.process_pid = -1
        Thread.__init__(self)

    def signal_thread_stop(self):
        self._stop_thread = True

    def listProcessesAndGetPid(self,process_name):
        try:
            process_list = self.test_dev.device.sh('ps').split('\r\r')

            for lines in process_list:
                temp = lines.split()
                if (len(temp) == 9) and temp[8] == str(process_name):
                    self.process_pid = temp[1] #The second item is the pid of the process
                    #print'Pid of process '+str(process_name)+':'+str(self.process_pid)
                    break

        except Exception, e:
            print str(e)

    def run(self):
        temp = 1
        retries = 0

        while(temp == 1):
            try:
                self.listProcessesAndGetPid(self.process_name)
                #Check if we have the process ID
                if self.process_pid == -1:
                    retries +=1
                    if retries > self.monitor_duration: #> 10 mins
                        print 'Giving up, unable to find pid of '+str(self.process_name)
                        return(-1)
                else:
                    break

                time.sleep(10)
            except Exception, e:
                print str(e)

        if (self.process_pid != -1):
            self.private_dirty_memory_command = 'dumpsys meminfo '+str(self.process_pid)
            self.heap_dump_command_1 = 'chmod 777 /data/misc'
            self.heap_dump_command_2 = 'kill -10 '+str(self.process_pid)
            self.pull_heap_logs_command = 'adb -s '+str(self.device_id)+' pull /data/misc '+str(self.log_directory)
            self.current_dirty_memory = 0

            while(temp == 1):
                time.sleep(self.monitor_duration)
                self.current_dirty_memory = 0
                if self._stop_thread == False: #Continue monitoring unless we are asked to stop
                    try:
                        self.dumpsys_output = self.test_dev.device.sh(str(self.private_dirty_memory_command)).split('\r\r')

                        if (self.dumpsys_output is not None):
                            for lines in self.dumpsys_output:
                                line = lines.split()

                                # ...
                                #    (priv dirty):     6152     4812     1860    12824
                                # ...
                                if (len(line) == 6) and ('priv' in line[0]):
                                    self.current_dirty_memory = line[5]
                                    print 'Current total private dirty memory:' + str(self.current_dirty_memory)
                                    break

                            #Check if the private dirty memory is >= trigger value and if it is dump it.

                            #Get the initial heap dump if the dirty memory is >= monitor value (First time only)
                            if  (self.first_watch_trigger == False) and (int(self.current_dirty_memory) >= int(self.initial_monitor_value)):
                                self.test_dev.device.sh(str(self.heap_dump_command_1))
                                self.test_dev.device.sh(str(self.heap_dump_command_2)) #Initial heap dump
                                os.system(str(self.pull_heap_logs_command))
                                self.first_watch_trigger = True
                            elif int(self.current_dirty_memory) >= int(self.trigger_value):
                                self.test_dev.device.sh(str(self.heap_dump_command_1))
                                self.test_dev.device.sh(str(self.heap_dump_command_2))
                                os.system(str(self.pull_heap_logs_command))

                    except Exception, e:
                        print 'Exception while monitoring process:'+str(self.process_name)
                        print str(e)

                else:
                    return(1)
class Launcher:
    def __init__(self, a):
        self.android = a

    def launch(self, func, loops, *args, **keywordargs):
        result, passes = func(loops, *args, **keywordargs)
        iteration_xml_string = "        <iteration attempts=\"%s\" passes=\"%s\"/>\n" % (str(loops), str(passes))
        android.log.log_report(xml = iteration_xml_string)
        return result


class KillApplication():
    def __init__(self,a):
        self.android = a
        self.Application_List = {
                                 'YouTube': 'com.google.process.gapps',
                                 'Maps': 'com.google.android.apps.maps',
                                 'Gmail': 'com.google.android.gm',
                                 'Market':'com.android.vending'
                                 }

    def kill_application(self,app_name):
        try:
            self.processes_list = self.android.device.sh('ps')
            self.temp_file = open('temp.txt','w')
            self.temp_file.write(self.processes_list)

            #Look for the specified app to get its pid
            self.temp_file = open('temp.txt','r')
            for lines in self.temp_file:
                match = re.match('(\w+)(\s*)(\d*)(.*)(\s)('+str(self.Application_List[app_name])+')',lines)

                if match is not None:
                    if match.group(6) == str(self.Application_List[app_name]):
                        self.pid_to_kill = match.group(3)

                        #Kill the app now that we have the pid
                        print 'Terminating application:'+str(app_name)
                        self.kill_string = 'kill '+str(self.pid_to_kill)
                        self.android.device.sh(self.kill_string)
                        print 'Process #'+str(self.pid_to_kill)+' terminated...'
                        self.temp_file.close()
                        break

        except Exception, e:
            print str(e)

class sendATCMDException(Exception):
    pass


class SetupDeviceConnections():

    def __init__(self):
        pass


    def initializeTestDevice(self):
        self.device_id = android.settings.DEVICES['TestDevice']['id']
        self.id2=self.device_id.split(':')[0]
        #os.system("adb connect %s"%self.id2)
        try:
            pass
            #print cmd1
            '''self.device_ids = cmd1.readlines()[1:-1]
            if (len(self.device_ids)==1 and 'device' in str(self.device_ids) ):
                self.device_id = self.device_ids[0].split('\t')[0]
            cmd1.close()'''
        except:
            print 'Failed to get adb devices.\n' 
        try:
            Android_Test_Device = android.connect(self.device_id)
        except Exception, e: 
            print "Fail to connect the devices!"
            print e
            Android_Test_Device = android.connect(self.device_id)
        #Android_Test_Device = android.connect(id=android.settings.DEVICES['TestDevice']['id'])
        return(Android_Test_Device)
        


class StabDL():

    def __init__(self, a):
        self.android = a

    TAG  = 'stabdeb'
    TAG1 = 'stabexc'

    e = None
    BP_PANIC = 'adb is unable to find'






    def slog_error(self, message):
        self.android.log.error(self.TAG1, message)
        #print '[', self.TAG1, ']', message
        #self.script_log.write(message)

    def slog_debug(self, message):
        self.android.log.debug(self.TAG, message)
        #print '[', self.TAG, ']', message
        #self.script_log.write(message)

    def slog_excep(self, message, iteration = " "):
        #print '[', self.TAG1, ']', message
        self.android.log.debug(self.TAG1, 'stabException')
        self.android.log.debug(self.TAG1,  message)
        exc_type, exc_value, exc_traceback=sys.exc_info()
        info = traceback.format_tb(exc_traceback)
        self.android.log.debug(self.TAG1, str(info))
        #if iteration != None:
        xml_string = "        <iteration_fail iteration=\"%s\" exception=\"%s\"/>\n" % (str(iteration), str(message).replace('<','').replace('>',''))
        android.log.log_report(xml = xml_string)

    def open_app_dt( self, app ) :
        for op in range ( 0, 3 ) :
            try :
                self.android.ui.unlock()
                self.android.input.back(3)
                time.sleep(2)
                if self.open_intent(app) == False:
                    raise Exception
                return True
            except :
                self.slog_excep( "open_app_dt" )
                if op == 2 :
                    return False

    def open_app( self, app ):
        for op in range ( 0, 3 ) :
            try :
                self.android.input.back(3)
                if self.open_intent(app) == False:
                    raise Exception
                return True
            except:
                self.slog_excep( "open_app" )
                if op == 2 :
                    return False

    def time_idle( self ):
        try :
            start_t = "Start : %s" % time.ctime()
            self.slog_debug( start_t )
            print start_t
            print "Sleeping for Idle time : "+str(LOOP_IDLE/3600)+" hours"
            self.slog_debug('Sleeping for Idle time : 10800(3hrs) ')
            time.sleep( LOOP_IDLE )
            end_t = "End   : %s" % time.ctime()
            print end_t
            self.slog_debug( end_t )

        except :
            self.slog_excep( "TIME_IDLE" )

    def open_intent(self,IconName):

        try:
            if IconName == 'ManuSearch':
                self.android.device.sh('am start -n mstar.tvsetting.ui/mstar.tvsetting.ui.Atvmanualtuning')
                time.sleep(2)
                assert "mstar.tvsetting.ui/mstar.tvsetting.ui.Atvmanualtuning" in self.android.ui.window()
                return True
            
            if IconName == 'AutoSearch':
                self.android.device.sh('am start -n mstar.tvsetting.ui/mstar.tvsetting.ui.Channeltuning')
                time.sleep(2)
                assert "mstar.tvsetting.ui/mstar.tvsetting.ui.Channeltuning" in self.android.ui.window()
                return True
            if IconName == 'Auto':
                self.android.device.sh('am start -n mstar.tvsetting.ui/mstar.tvsetting.ui.AutoTuneOptionActivity')
                time.sleep(2)
                assert "mstar.tvsetting.ui/mstar.tvsetting.ui.AutoTuneOptionActivity" in self.android.ui.window()
                return True
            if IconName == 'ATV':
                self.android.device.sh('am start -n mstar.tvsetting.ui/mstar.tvsetting.ui.RootActivity')
                time.sleep(2)
                assert "mstar.tvsetting.ui/mstar.tvsetting.ui.RootActivity" in self.android.ui.window()
                return True
            if IconName == 'OnlineTV':
                self.android.device.sh('am start -a android.intent.category.LAUNCHER -n com.letv.t2.onlinetv/com.letv.t2.onlinetv.OnlineTVActivity')
                time.sleep(2)
                assert "com.letv.t2.onlinetv/com.letv.t2.onlinetv.OnlineTVActivity" in self.android.ui.window()
                return True
            elif IconName == 'NetPlayer':
                self.android.device.sh('am start -a android.intent.category.LAUNCHER -n com.android.letv05111533/com.android.letv05111533.NetPlayer')
                time.sleep(2)
                assert "com.android.letv05111533/com.android.letv05111533.NetPlayer" in self.android.ui.window()
                return True  
            elif IconName == 'Letv':
                #self.android.device.sh('am start -a android.intent.category.LAUNCHER -n com.letv.t2.launcher/com.letv.t2.launcher.T2LauncherActivity')
                self.android.device.sh('am start -a android.intent.category.LAUNCHER -n com.letv.livetv/com.letv.livetv.LiveTvActivity')
                time.sleep(2)
                assert "com.letv.livetv/com.letv.livetv.LiveTvActivity" in self.android.ui.window()
                return True 
            elif IconName == 'Settings':
                self.android.device.sh('am start -a android.intent.category.LAUNCHER -n com.android.settings/com.android.settings.Settings')
                time.sleep(2)
                assert "com.android.settings/com.android.settings.Settings" in self.android.ui.window()
                return True  
            elif IconName == 'Filesystem':
                self.android.device.sh('am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -f 0x10200000 -n com.letv.filemanager/.FileExplorerTabActivity')
                time.sleep(2)
                assert "com.letv.filemanager/com.letv.filemanager.FileExplorerTabActivity" in self.android.ui.window()
                return True
            elif IconName == 'OnlineUpgrade':
                self.android.device.sh('am start -a android.intent.category.LAUNCHER -n com.letv.systemupgrade/com.letv.systemupgrade.SystemUpgradeActivity')
                self.android.device.sh('am start -a android.intent.category.LAUNCHER -n com.stv.systemupgrade/com.stv.systemupgrade.SystemUpgradeActivity')
                time.sleep(2)
                assert "com.letv.systemupgrade/com.letv.systemupgrade.SystemUpgradeActivity" in self.android.ui.window()
                return True       
            
          
            else:
                return False
        except:
            return False
           
           
           


import android
def __test_callback(android):
    android.stab     = StabDL(android)

 

android.register_module_callback(__test_callback)

