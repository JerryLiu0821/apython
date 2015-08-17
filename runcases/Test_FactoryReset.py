
#!/usr/bin/env python
import os
import sys
import datetime
import subprocess
import re
import time

###############################################################################
#Configure these variables                                                    #
###############################################################################
#set this variable to the number of loops you want to run
loop = 1
#set this variable to the name of the custom type of rack
custom_type = 'Custom'

#set this variable to the location of the stabrackSettings.py file
rack_settings = 'stabrackSettings.py'
config_file = 'TV2.py' 

#set this variable to the location you want the logs to be wrote to
path_to_logs = os.path.join('..','Log_FactoryReset') 

#set this variable to the name of the list file to use
#test_case_list =  os.path.join('..','List','List_PlayServerVideos' )
test_case_list =  os.path.join('List','list_factoryreset' )


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

runtests = os.path.join('..','testcases', 'interface','runtests.py')

def root_device():
    print "Attempting to root device"
    device_config_import = __import__(config_file.strip('.py'))
    device_serial_number = device_config_import.DEVICES['TestDevice']['id']
    try:
        cmd1 = os.popen ('adb devices')
        device_ids = cmd1.readlines()[1:-1]
        if (len(device_ids)==1 and 'device' in str(device_ids) ):
            device_serial_number = device_ids[0].split('\t')[0]
        cmd1.close()
    except:
        print 'Failed to get adb devices.\n' 
    
    root_cmd = 'adb -s %s root' % device_serial_number
    print root_cmd
    process = subprocess.Popen(root_cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
    (stdout, stderr) = process.communicate()
    print stdout
    print stderr
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

def run_tests():

    if os.name == 'posix':
        settings_delimeter = ':'
    else:
        settings_delimeter = ';'
    
    runtests = os.path.join('..','testcases', 'interface','runtests.py')
    
    #os.system("python logcat.py");
	
    run_script_list(setup_language_scripts)
    for x in range (1,loop+1):
        run_script_list(pre_loop_scripts)
        print '\n******************Starting Loop %d*************************\n' % x
        os.system ('python %s --settings %s%s%s --rack-type 1 --custom-type %s  --report-parent-dir %s --run %s' % (runtests, config_file, settings_delimeter, rack_settings,custom_type, path_to_logs, test_case_list))
        run_script_list(post_loop_scripts)

    raw_input ("Test Completed - Total Loops Completed %d : Press Enter to Exit..." % x)



def main():
    root_device() 
    run_tests()

if __name__ == "__main__":
    main()
