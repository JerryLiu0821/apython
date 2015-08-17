import android, time, unittest, sys


import re
import os
import traceback


from threading import Thread #To check heap usage



LOOP_IDLE = 10  #Seconds

MADGPENNYTOSS_INSTALLED = 0
MADGCHICKEN_INSTALLED = 0
MADGHORSE_INSTALLED = 0

MENU_DELAY = 10

SERIAL_INTERFACE = None

class MonitorMemoryUsage(Thread): #For any applications, threads etc... which have a process id.
    def __init__(self,test_dev,process_name,initial_monitor_value,trigger_value, monitor_duration):
        self.test_dev = test_dev
        self.process_name = str(process_name)
        self.device_id = android.settings.DEVICES['TestDevice']['id']
        try:
            cmd1 = os.popen ('adb devices')
            self.device_ids = cmd1.readlines()[1:-1]
            if (len(self.device_ids)==1 and 'device' in str(self.device_ids) ):
                self.device_id = self.device_ids[0].split('\t')[0]
            cmd1.close()
        except:
            print 'Failed to get adb devices.\n' 
        
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
        try:
            cmd1 = os.popen ('adb devices')
            self.device_ids = cmd1.readlines()[1:-1]
            if (len(self.device_ids)==1 and 'device' in str(self.device_ids) ):
                self.device_id = self.device_ids[0].split('\t')[0]
            cmd1.close()
        except:
            print 'Failed to get adb devices.\n' 
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
        """Intents for Kobe's apps listed on the main menu"""

        try:
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
                self.android.device.sh('am start -a android.intent.category.LAUNCHER -n com.letv.t2.launcher/com.letv.t2.launcher.T2LauncherActivity')
                time.sleep(2)
                assert "com.letv.t2.launcher/com.letv.t2.launcher.T2LauncherActivity" in self.android.ui.window()
                return True 
            elif IconName == 'Settings':
                self.android.device.sh('am start -a android.intent.category.LAUNCHER -n com.android.settings/com.android.settings.Settings')
                time.sleep(2)
                assert "com.android.settings/com.android.settings.Settings" in self.android.ui.window()
                return True   
            elif IconName == 'TestKeys':
                self.android.device.sh('am start -a android.intent.category.LAUNCHER -n com.example.testkeyevent/com.example.testkeyevent.TestKeyActivity')
                time.sleep(2)
                assert "com.example.testkeyevent/com.example.testkeyevent.TestKeyActivity" in self.android.ui.window()
                return True
        
            else:
                return False
        except:
            return False
           
           
           


import android
def __test_callback(android):
    android.stab     = StabDL(android)

 

android.register_module_callback(__test_callback)

