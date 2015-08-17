
#!/usr/bin/env python
import os
import sys
import datetime
import subprocess
import re
import time
import threading
import commands


#two param should be given
#which script you will running; which device you want to start
###############################################################################
#Configure these variables                                                    #
###############################################################################
#set this variable to the number of loops you want to run
loop = 1
#set this variable to the name of the custom type of rack
custom_type = 'Custom'

#set this variable to the location of the stabrackSettings.py file
rack_settings = 'stabrackSettings.py'
config_file = 'TV/'+sys.argv[2] 

#set this variable to the location you want the logs to be wrote to 
path_to_logs = os.path.join('..','Log',sys.argv[3]) 

#set this variable to the name of the list file to use
#test_case_list =  os.path.join('..','List','List_PlayServerVideos' )
test_case_list =  os.path.join('List',sys.argv[1] )

#set this variable to the folder containing the product specific files
product_specific_scripts_location = os.path.join('..','testcases', 'setup')

#this list contains scripts named in a string to run before tests start
#setup_language_scripts = ['SetupLanguage.py']
setup_language_scripts = ['']

#this list contains scripts named in a string to run before each loop
pre_loop_scripts = []

#this list contains scripts named in a string to run after each loop
post_loop_scripts = ['PreLoop.py']

#set this variable to the name of the folder to write pretest, preloop, and preloop logs
other_tests_folder = 'OtherScripts'


package_location = "."


###############################################################################
#Do not touch any of the code below this                                      #
###############################################################################

if os.name == 'posix':
    settings_delimeter = ':'
else:
    settings_delimeter = ';'

runtests = os.path.join('..','apython','runtests.py')

def shell(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdout, stderr) = p.communicate()
    return (stdout, stderr)

class checkAdbStatusThread(threading.Thread):
    def __init__(self,id):
        threading.Thread.__init__(self)
        self.id = id
    def run(self):
        while True:
            status = ''
            result,status = shell('adb -s %s shell getprop | grep ro.letv.release.date' %self.id)
            if 'error' in status:
                print 'adb disconnect ' + self.id
                shell('adb disconnect '+self.id)
                root_device(self.id)
            time.sleep(60)

def connect_device(func):
    def connect(id):
        out, err = shell('adb devices')
        print out
        if id not in out:
            print 'connect devices'
            shell('adb connect '+id)
            time.sleep(2)
        func(id)
    return connect

@connect_device
def root_device(id):
    print "Attempting to root device"
    root_cmd = 'adb -s %s root' %id
    print root_cmd
    stdout,stderr = shell(root_cmd)
    if 'already' not in stdout:
        time.sleep(5)      
                    
def run_script_list(script_list):
    for script in script_list:
        script_location = os.path.join(product_specific_scripts_location, script)
        if os.path.isfile(script_location):
            non_test_log_location = os.path.join(path_to_logs, other_tests_folder)
            cmd = 'python %s --settings %s%s%s --rack-type 1 --custom-type %s --report-parent-dir %s %s' % (runtests, config_file, settings_delimeter, rack_settings, custom_type, non_test_log_location, script_location) 
            print cmd
            os.system(cmd)

class captureMeminfo(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.id = id

    def getPath(self):
        try:
            fhost = os.popen("hostname")
            hostname = fhost.readline()
            hostname = hostname.strip()
            fhost.close()
            path = os.path.join(path_to_logs, hostname)
        except:
            print "Fail to get PC name\n"
        logDir = commands.getoutput("ls %s | grep report"%path)
        if logDir != "":
            path = os.path.join(path, logDir)
        return path
    def run(self):
        time.sleep(5)
        while True:
            dirp = self.getPath()
            os.system('adb -s %s shell procrank >> %s' %(self.id, os.path.join(dirp, "procrank.log")))
            os.system('adb -s %s shell dumpsys meminfo >> %s' %(self.id, os.path.join(dirp, "dumpsys_meminfo.log")))
            """
            mtime = commands.getoutput('adb -s %s shell date'%self.id)
            minifree = commands.getoutput('adb -s %s shell cat /sys/module/lowmemorykiller/parameters/minfree'%self.id)
            adj = commands.getoutput('adb -s %s shell cat /sys/module/lowmemorykiller/parameters/adj'%self.id)
            procrank = commands.getoutput('adb -s %s shell procrank'%self.id)
            free = commands.getoutput('adb -s %s shell busybox free'%self.id)
            meminfo = commands.getoutput('adb -s %s shell cat /proc/meminfo'%self.id)
            mali_memory = commands.getoutput('adb -s %s shell cat /sys/kernel/debug/mali/memory_usage'%self.id)
            ump_memory = commands.getoutput('adb -s %s shell cat /sys/kernel/debug/ump/memory_usage'%self.id)
            top = commands.getoutput('adb -s %s shell busybox top -n 1' %self.id)
            fp = open(os.path.join(self.getPath(), "meminfo.log"),'a+')
            try:
                fp.writelines("\n%s\n" %mtime)
                fp.writelines("\nLMK: minfree:\n")
                fp.writelines(minifree)
                fp.writelines("\nLMK: adj:\n")
                fp.writelines(adj)
                fp.writelines("\nprocrank:\n")
                fp.writelines(procrank)
                fp.writelines("\ntop:\n")
                fp.writelines(top)
                fp.writelines("\nbusybox free:\n")
                fp.writelines(free)
                fp.writelines("\ncat /proc/meminfo:\n")
                fp.writelines(meminfo)
                fp.writelines("\nmali memory_usage:\n")
                fp.writelines(mali_memory)
                fp.writelines("\nump memory_usage:\n")
                fp.writelines(ump_memory)
                fp.writelines('\n================================\n')
                fp.close
            except:fp.close()
            finally:fp.close()
            """
            time.sleep(60)

class draw(object):
    def __init__(self,path):
        self.path = path
        self.procrank = os.path.join(path,"procrank.log")
        if not os.path.exists(self.procrank):
            return
        else:
            os.system("dos2unix %s" %self.procrank)

    def list_Pss(self, processname):
        total_pss = []
        with open(self.procrank, "r") as fp:
            for line in fp:
                match_pss = re.compile(r'.*\s+(\d+)K\s+\d+K\s+%s$' %processname).match(line)
                if match_pss:
                    o = match_pss.group(1)
                    total_pss.append(int(o))
        return total_pss

    def getTop(self):
        with open(self.procrank, "r") as fp:
            all_lines = fp.readlines()
            lines = []
            times = 0
            for i in range(len(all_lines)):
                m = re.search(r'(\s+PID\s+Vss\s+Rss\s+Pss\s+Uss\s+cmdline)',all_lines[i])
                if m:
                    times += 1
                    for j in range(1, 10):
                        lines.append(all_lines[i+j])
            pname=[]
            for line in lines:
                m = re.search(r'(?P<PID>\d+)\s+(?P<Vss>\d+K)\s+(?P<Rss>\d+K)\s+(?P<Pss>\d+K)\s+(?P<Uss>\d+K)\s+(?P<Pname>\S+)',line)
                if m:
                    pname.append(m.groupdict()['Pname'])
    
            l = list(set(pname))
            return l

    def draw_line(self):
        try:
            import pygal
        except:
            return
        #draw TOTAL
        total = self.list_Pss("TOTAL")
        length = len(total)
        lchart = pygal.Line()
        lchart.title = "procrank analyze"
        lchart.x_title = "times/(60s)"
        lchart.y_title = "Pss(K)"
        lchart.width = 1200
        lchart.add("TOTAL", total)
        lchart.x_labels = map(str,range(length))
        lchart.render_to_file(os.path.join(self.path,"total_pss.svg"))
        #draw top 10
        prss = self.getTop()
        achart = pygal.Line()
        achart.title = "procrank analyze"
        achart.x_title = "times/(60s)"
        achart.y_title = "Pss(K)"
        achart.width = 1200
        achart.x_labels = map(str,range(length))
        for p in prss:
            achart.add(p, self.list_Pss(p))
        achart.render_to_file(os.path.join(self.path,"top_10_pss.svg"))


def run_tests():

    if os.name == 'posix':
        settings_delimeter = ':'
    else:
        settings_delimeter = ';'

    runtests = os.path.join('..','apython','runtests.py')

    run_script_list(setup_language_scripts)
    for x in range (1,loop+1):
        run_script_list(pre_loop_scripts)
        print '\n******************Starting Loop %d*************************\n' % x
        os.system ('python %s --settings %s%s%s --rack-type 1 --custom-type %s  --report-parent-dir %s --run %s' % (runtests, config_file, settings_delimeter, rack_settings,custom_type, path_to_logs, test_case_list))
        run_script_list(post_loop_scripts)

    #raw_input ("Test Completed - Total Loops Completed %d : Press Enter to Exit..." % x)



def main():
    serial_no = config_file.replace('/','.')
    device_serial_number =getattr(__import__(serial_no.strip('.py')),serial_no.split('.')[1]).DEVICES['TestDevice']['id']
    root_device(device_serial_number) 
    t=checkAdbStatusThread(device_serial_number)
    t.setDaemon(True)
    t.start()
    c=captureMeminfo(device_serial_number)
    c.setDaemon(True)
    c.start()
    run_tests()
    d = draw(c.getPath())
    d.draw_line()

if __name__ == "__main__":
    main()
