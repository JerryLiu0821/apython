
#!/usr/bin/env python
import os
import sys
import datetime
import subprocess
import re
import time
import threading

###############################################################################
#Configure these variables                                                    #
###############################################################################
#set this variable to the number of loops you want to run
loop = 1
#set this variable to the name of the custom type of rack
custom_type = 'Custom'

#set this variable to the location of the stabrackSettings.py file
rack_settings = 'stabrackSettings.py'
config_file = 'TV/TV3.py' 

#set this variable to the location you want the logs to be wrote to 
path_to_logs = os.path.join('..','Log_Cloud_Daily') 

#set this variable to the name of the list file to use
#test_case_list =  os.path.join('..','List','List_PlayServerVideos' ) 
test_case_list =  os.path.join('List','list_cloudvideo' ) 

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

runtests = os.path.join('..','apython','runtests_cloud.py')

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
                print 'adb disconnect '+self.id
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
    def __init__(self, id,dirp):
        threading.Thread.__init__(self)
        self.id = id
        if not os.path.exists(dirp):os.mkdir(dirp)
        self.today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        self.dump_mem = os.path.join(dirp,'dumpsys_meminfo_' +time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time())))
        self.procrank = os.path.join(dirp,'procrank_'+time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time())))
        self.top = os.path.join(dirp,'top_'+time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time())))
        print self.dump_mem, self.procrank, self.top
    def run(self):
        while True:
            o_d,e_d = shell('adb -s %s shell dumpsys meminfo' %self.id)
            o_p,e_p = shell('adb -s %s shell procrank' %self.id)
            o_t,e_t = shell('adb -s %s shell busybox top -n 1' %self.id)
            if o_d !=None and o_d != '':
                fp = open(self.dump_mem,'a+')
                try:
                    fp.writelines(o_d)
                    fp.write('================================ \n')
                    fp.close
                except:fp.close()
                finally:fp.close()
            else:pass
            if o_p !=None and o_p!='':
                fp = open(self.procrank,'a+')
                try:
                    fp.writelines(o_p)
                    fp.write('================================ \n')
                    fp.close
                except:fp.close()
                finally:fp.close()
            else:pass
            if o_t !=None and o_t!='':
                fp = open(self.top,'a+')
                try:
                    fp.writelines(o_t)
                    fp.write('================================ \n')
                    fp.close
                except:fp.close()
                finally:fp.close()
            else:pass
            time.sleep(600)           

def run_tests():

    if os.name == 'posix':
        settings_delimeter = ':'
    else:
        settings_delimeter = ';'
    
    runtests = os.path.join('..','apython','runtests_cloud.py')
    
    run_script_list(setup_language_scripts)
    for x in range (1,loop+1):
        run_script_list(pre_loop_scripts)
        print '\n******************Starting Loop %d*************************\n' % x
        os.system ('python %s --settings %s%s%s --rack-type 1 --custom-type %s  --report-parent-dir %s --run %s' % (runtests, config_file, settings_delimeter, rack_settings,custom_type, path_to_logs, test_case_list))
        run_script_list(post_loop_scripts)



def main():
    serial_no = config_file.replace('/','.')
    device_serial_number =getattr(__import__(serial_no.strip('.py')),serial_no.split('.')[1]).DEVICES['TestDevice']['id']
    root_device(device_serial_number) 
    t=checkAdbStatusThread(device_serial_number)
    t.setDaemon(True)
    t.start()
    c=captureMeminfo(device_serial_number,'./meminfo')
    c.setDaemon(True)
    c.start()
    run_tests()

if __name__ == "__main__":
    main()
