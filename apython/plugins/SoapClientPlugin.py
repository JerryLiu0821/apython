
class SoapClientPlugin(nose.plugins.Plugin):
    name = 'Soap-Client'

    def options(self, parser, env):
        nose.plugins.Plugin.options(self, parser, env)
        parser.add_option('--rack-type', action='store',
                dest='rack_type',
                default=None,
                help= "Determines if it is an official or Test rack to for prgoram name.")
        parser.add_option('--file-name', action='store',
                dest='filename',
                default='filenotfound.py',
                help= "Create a backup of missed entries in database so we can add them later.")
        parser.add_option('--custom-type', action='store',
                dest='custom_type',
                default='Custom',
                help= "Used to identify custom application stability rack. So making it easier to get the racks only that you need.")

    def configure(self, options, conf):
        nose.plugins.Plugin.configure(self, options, conf) 
    if options.rack_type == None:
            self.enabled = False
            return
        else:
            self.enabled = True
        self.passed = 0
        self.test_number = 0
        self.rack_type = options.rack_type if options.rack_type != None else 5
        self.filename = options.filename
        self.custom_type = options.custom_type
        self.custom_type = self.custom_type.strip()
        self.failure = 0
 
    def startTest(self, test):
        import datetime

        self.test_number += 1
        self.test_address = test.address()
        self.test_class = test.id()
        self.test_name = test.shortDescription() or test.id()
        self.test_result = None
        self.test_start_time = datetime.datetime.now().replace(microsecond=0)
        self.reports_start = self.test_start_time.strftime("%Y-%m-%d %H:%M:%S")

        if os.name == "posix":
            log_path = 'logs/%05d/' % ( self.test_number )
        else:
            log_path = 'logs\\%05d\\' % ( self.test_number )
        self.path = os.path.join(android.log.report_directory(), log_path)
        print '\n' + os.path.abspath(self.path)

    def stopTest(self, test):
        import datetime
        self.reports = []
        test_end_time = datetime.datetime.now().replace(microsecond=0)
        self.reports_end = test_end_time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_time_app = test_end_time.strftime("%Y_%m_%d_%H_%M_%S")

        self.test_run_time = test_end_time-self.test_start_time

        self.reports.append( {
                        'name':self.test_name,
                        'start_time':self.reports_start,
                        'end_time':self.reports_end,
                        'result':self.test_result
                         } )

        # generate report to be used by Soap client
        self.generate_report()

    def addSuccess(self, test):
        self.passed += 1
    self.test_result = 'PASS'

    def addErrorOrFailure(self, test, err, type):
    TAG = 'exception'
    self.test_result = type
    test_err = self.formatErr(err)
    android.log.error('test', test_err)
    android.log.log_report(html='<br>'.join(test_err.splitlines()))

    android.log.error(TAG,
                        '\n' +
                        '=============================\n' +
                        '== STACK TRACE\n' +
                        '=============================\n' +
                        traceback.format_exc())

    global connected_devices
    if connected_devices:
        for a in connected_devices:
            # This is a crude way to try to avoid starting the view server
            # in the exception logger.
            if a.internal.transport.view_server_port() >= 0:
                try:
                    if sys.exc_type in [ android.ui.WaitforTimeout, android.ui.WidgetNotFound ]:
                        s = a.ui.screen()
                        a.log.error(TAG,
                                '\n' +
                                '=============================\n' +
                                '== SCREEN WIDGETS\n' +
                                '=============================\n' +
                                repr(s) )

                    log_screenshot(a, TAG, 'screenshot',
                            traceback.format_exc(),
                            caption_report='Screen after exception<br />')
                except KeyboardInterrupt:
                    raise
                except:
                    # If the device is disconnected, this will cause a
                    # failure in the exception handler.
                    # XXX: Don't call log_filename until the screenshot
                        # is known to be successful
                    pass

    def addError(self, test, err): self.addErrorOrFailure(test, err, 'ERROR')


    def addFailure(self, test, err): self.addErrorOrFailure(test, err, 'FAIL')

    def generate_report(self, result=None):

        self.current_FC = 0
        self.current_ANR = 0
        self.current_ANR_SEARCH = 0
        self.current_ANR_INFO = 0
        self.current_Tomb =0
        self.current_BP = 0
        self.current_Kernel = 0
        self.current_Kernel_SEARCH = 0
        self.current_Kernel_INFO = 0
        self.current_Test = 0
        self.current_SYSSERVER = 0

        #self.id = 
        self.id = android.settings.DEVICES['TestDevice']['id']

        try:
            cmd1 = os.popen ('adb devices')
            self.device_ids = cmd1.readlines()[1:-1]
            if (len(self.device_ids)==1 and 'device' in str(self.device_ids)):
                self.id = self.device_ids[0].split('\t')[0]
            cmd1.close()
        except:
            print 'Failed to get adb devices.\n' 
        #result_file = 'result_%s.txt' % ( self.id )
        #file = open(result_file, 'a')

        try:
            #clearing the log buffer
            os.system ('adb -s '+ self.id + ' logcat -c')
        except:
            print 'Looks like the device is disconnected !! check device connectivity\n'
        try:
            cmd2 = os.popen ('hostname')
            self.hostname = cmd2.readline()
            self.hostname = self.hostname.strip()
            cmd2.close()
        except:
            print 'Failed to get PC Name - Something is wierd\n'            
            

        try:
            cmd5 = os.popen ('adb -s '+ self.id + ' shell getprop ro.product.device')
            self.deviceType = cmd5.readline()
            self.deviceType = self.deviceType.strip()
            cmd5.close()
        except:
            print 'Failed to get product type from device - Check if shell inactive or phone disconnected\n'            

        try:
            cmd6 = os.popen ('adb -s '+ self.id + ' shell getprop ro.build.version.release')
            self.release = cmd6.readline()
            self.release = self.release.strip()
            cmd6.close()
        except:
            print 'Failed to get build version from device - Check if shell inactive or phone disconnected\n'

        if self.rack_type == '1':
                self.program = self.deviceType+'_'+self.release
        if self.rack_type == '2':
                self.program = self.deviceType+'_'+self.release+'_Test'
        if self.rack_type == '3':
                self.program = self.deviceType+'_'+self.release+'_Plat'
        if self.rack_type == '4':
                self.program = self.deviceType+'_'+self.release+'_Health'
        if self.rack_type == '5':
                self.program = self.deviceType+'_'+self.release+'_'+self.custom_type
        if self.rack_type == '6':
                self.program = self.deviceType+'_'+self.release+'_Sanity'

        import socket
        import shutil
        import subprocess



        try:
            cmd3 = os.popen ('adb  -s '+ self.id + ' shell getprop ro.build.id')
            self.swver = cmd3.readline()
            cmd3.close()
        except:
           
            print 'Failed to get software version, please check device connectivity\n' 

        try:
            cmd1 = os.popen ('adb -s '+ self.id + ' shell getprop ro.serialno')
            self.barcode = cmd1.readline()
            self.barcode = self.barcode.rstrip("\n")
            self.barcode = self.barcode[:-1]
            cmd1.close()
           
        except:
            print 'Failed to get Barcode from device - Check if shell inactive or phone disconnected\n'            

        try:
            logcat_main = 'logcat_main.%s.1.txt' % ( self.id )
            self.logcat_path = os.path.join(self.path, logcat_main)
            #Counting the number of occurrences of failures.
            self.current_FC = open (self.logcat_path).read().count("thread exiting with uncaught exception")
            self.current_ANR_SEARCH = open (self.logcat_path).read().count("ActivityManager: ANR in ")
            self.current_ANR_INFO = open (self.logcat_path).read().count("ActivityManager: ANR information:")
            self.current_Tomb = open (self.logcat_path).read().count("Build fingerprint")
            self.current_Kernel_SEARCH = open (self.logcat_path).read().count("/data/dontpanic/apanic_console")
            self.current_Kernel_INFO = open (self.logcat_path).read().count("Nothing for /data/dontpanic/apanic_console")
            self.current_BP = open (self.logcat_path).read().count("panic_daemon: bp panic!")
            self.current_SYSSERVER = open (self.logcat_path).read().count("WATCHDOG IS KILLING")
            self.current_ANR = self.current_ANR_SEARCH - self.current_ANR_INFO
            self.current_Kernel = self.current_Kernel_SEARCH - self.current_Kernel_INFO
        except:
            print 'Cannot find logcat - Please make sure the scripts are running fine: Either a file is not updated properly or a file is missing\n'

        import re
        DEVICELOGS_FOLDER_NAME = 'devicelogs'
        BP_PANIC_FOLDERS = [ "data/panic", "data/panicreports" ]
        AP_PANIC_FOLDERS = [ "data/dontpanic", "data/kernelpanics", "data/kernel_panics" ]
        BP_FILENAME_STRING = "^bp_panic|^modem.log|^bppanic|^qmodem_panic0"
#        AP_FILENAME_STRING = "^apanic_console|^last_kmsg"
        AP_FILENAME_STRING = "^apanic_console"
        BP_PANIC_NAME_SRE = re.compile( BP_FILENAME_STRING )
        AP_PANIC_NAME_SRE = re.compile( AP_FILENAME_STRING )

        found_bp_panic_file = False
        found_ap_panic_file = False

        def _isPanicFile( fileName, regex ):
            return regex.match( fileName ) is not None
        
        try:
            devicelogspath = os.path.join( self.path, DEVICELOGS_FOLDER_NAME )
            for bpentry in BP_PANIC_FOLDERS:
                bp_panic_path = os.path.join( devicelogspath, bpentry )
                if os.path.exists( bp_panic_path ):
                    for thing in os.listdir( bp_panic_path ):
                        if (not found_bp_panic_file) and _isPanicFile( thing, BP_PANIC_NAME_SRE ):
                            self.current_BP += 1
                            found_bp_panic_file = True

            for apentry in AP_PANIC_FOLDERS:
                ap_panic_path = os.path.join( devicelogspath, apentry )
                if os.path.exists( ap_panic_path ):
                    for thing in os.listdir( ap_panic_path ):
                        if (not found_ap_panic_file) and _isPanicFile( thing, AP_PANIC_NAME_SRE  ):
                            self.current_Kernel += 1
                            found_ap_panic_file = True
        except:
            print 'Cannot find devicelogs folder'
        
        '''try:
                for rack_result in self.reports:
                        file.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%d" "%d" "%d" "%d" "%d" "%d"\n' %
                                ( self.hostname ,self.barcode ,rack_result['name'].split('|')[0].strip(),
                                rack_result['name'].split('|')[1].strip() if ('|' in rack_result['name']) else rack_result['name'],
                                rack_result['start_time'],rack_result['end_time'],
                                self.test_run_time, rack_result['result'],self.current_FC,self.current_ANR,self.current_Tomb,self.current_Kernel,self.current_BP,self.current_SYSSERVER ))
                try:
                    # Adding values to variables
                    self.record.rack = '%s' % self.hostname
                    self.record.version = '%s' % self.blur
                    self.record.gitsha = '%s' % self.commit_id
                    self.record.script = '%s' % rack_result['name'].split('|')[0].strip()
                    self.record.start_time = '%s' % rack_result['start_time']
                    self.record.end_time = '%s' % rack_result['end_time']
                    self.record.fc = '%d' % self.current_FC
                    self.record.anr = '%d' % self.current_ANR
                    self.record.ts = '%d' % self.current_Tomb
                    self.record.kernel = '%d' % self.current_Kernel
                    self.record.bp = '%d' % self.current_BP
                    self.record.ss = '%d' % self.current_SYSSERVER
                    self.record.program = '%s' % self.program
                    self.record.barcode = '%s' % self.barcode
                    self.record.result = '%s' % rack_result['result']
                    self.rec_number = self.client.service.addRecord(self.record)
                except:
                    print 'Failed to add record !! Please check if server is in trouble\n'
                    print 'Creating a backup of the record in %s so it could be added later after test execution\n' % self.filename
                    backup = open (self.filename, 'a')
                    backup.write ('\n######## Adding a new record that has been skipped ##############\n')
                    backup.write ('record.rack = \'' + self.hostname +'\'\n')
                    backup.write ('record.version = \'' + self.blur +'\'\n')
                    backup.write ('record.gitsha = \'' + self.commit_id +'\'\n')
                    backup.write ('record.script = \'' + rack_result['name'].split('|')[0].strip() + '\'\n')
                    backup.write ('record.start_time = \'' + rack_result['start_time'] + '\'\n')
                    backup.write ('record.end_time = \'' + rack_result['end_time'] + '\'\n')
                    backup.write ('record.fc = \'' + str(self.current_FC) + '\'\n')
                    backup.write ('record.anr = \'' + str(self.current_ANR) + '\'\n')
                    backup.write ('record.ts = \'' + str(self.current_Tomb) + '\'\n')
                    backup.write ('record.kernel = \'' + str(self.current_Kernel) + '\'\n')
                    backup.write ('record.bp = \'' + str(self.current_BP) + '\'\n')
                    backup.write ('record.ss = \'' + str(self.current_SYSSERVER) + '\'\n')
                    backup.write ('record.program = \'' + self.program + '\'\n')
                    backup.write ('record.barcode = \'' + self.barcode + '\'\n')
                    backup.write ('record.result = \'' + rack_result['result'] + '\'\n')
                    backup.write ('try:\n')
                    backup.write ('    rec_number = client.service.addRecord(record)\n')
                    backup.write ('    print \'Record Added Successfully\'\n')
                    backup.write ('except:\n')
                    backup.write ('    print \'Looks like the server is still down or the url you are using is wrong please try again later. Do not delete this file yet\'\n\n')
                    backup.close()
                    print 'Backup file created successfully - Please run this file after the execution is completed\n'
                try:
                    self.client.service.startRun(self.hostname,self.ip)
                except:
                    print 'Failed to map ip with PC !! Check if server is in trouble\n'
                    backup = open (self.filename, 'a')
                    backup.write ('try:\n')
                    backup.write ('    client.service.startRun(\''+ self.hostname + '\',\'' + self.ip + '\')\n')
                    backup.write ('    print \'IP mapping successfull\'\n')
                    backup.write ('except:\n')
                    backup.write ('    print \'Looks like the server is still down. Try again after sometime\'\n\n')
                    backup.close()
                    print 'Backup file created successfully - Please run this file after test execution is completed\n'
        finally:
                file.close()

        try:
            #Creating Directories for capturing crashlogs
            pwd = os.getcwd()
            #Getting the least significant digit out of the record number
            self.lsd = int(self.rec_number) % 10
        except:
            print 'Failed to get record number so the expected folder creation will fail !! Lets use Plan B\n'
       
        crash_log_folder = os.path.join(pwd, 'CrashLogs') 
        if not os.path.exists(crash_log_folder):
                os.makedirs(crash_log_folder)
        try:
            crash_log_folder_lsd = os.path.join(crash_log_folder, str(self.lsd))
            if not os.path.exists(crash_log_folder_lsd):
                os.makedirs(crash_log_folder_lsd)
            self.crash_directory = crash_log_folder_lsd
            logcat_move = 'logcat_%s_%s_%s.txt' % ( self.barcode, self.rec_number, self.log_time_app )
            anr_move = 'ANR_TRACES_%s_%s_%s.txt' % ( self.barcode, self.rec_number, self.log_time_app )
            self.traces_move = os.path.join(self.crash_directory, anr_move)

            if self.current_FC >= 1 or self.current_ANR >= 1 or self.current_Tomb >= 1 or self.current_Kernel >= 1 or self.current_BP >= 1 or self.current_SYSSERVER >= 1:
                print 'Copying the crashfile to the Crashlogs directory\n'
                shutil.copy2(self.logcat_path,os.path.join(self.crash_directory, logcat_move) )
            if self.current_ANR >= 1:
                print 'Copying the traces file to Crashlogs directory\n'
                subprocess.Popen (['adb','-s','%s' % self.id,'pull','/data/anr/traces.txt','%s' % self.traces_move])

        except:
            print 'Failed to move logs or create folder as record value not returned !! We may use a temporary folder to save the crash logs (if applicable) till it recovers\n'
            blur_folder = os.path.join(pwd, self.blurver)
            if not os.path.exists(blur_folder):
                os.makedirs(blur_folder)
            self.crash_directory = blur_folder
            logcat_move = 'logcat_%s_%s.txt' % ( self.barcode, self.log_time_app )
            anr_move = 'ANR_TRACES_%s_%s.txt' % ( self.barcode, self.log_time_app )
            self.traces_move = os.path.join(self.crash_directory, anr_move)

            if self.current_FC >= 1 or self.current_ANR >= 1 or self.current_Tomb >= 1 or self.current_Kernel >= 1 or self.current_BP >= 1 or self.current_SYSSERVER >= 1:
                print 'Copying the crashfile to the Temporary directory - they will be moved to original location once the backup file is executed\n'
                shutil.copy2(self.logcat_path, os.path.join(self.crash_directory, logcat_move) )
            if self.current_ANR >= 1:
                print 'Copying the traces file to Temporary directory - they will be moved to original location once the backup file is executed\n'
                subprocess.Popen (['adb','-s','%s' % self.id,'pull','/data/anr/traces.txt','%s' % self.traces_move])

            if self.current_FC >= 1 or self.current_ANR >= 1 or self.current_Tomb >= 1 or self.current_Kernel >= 1 or self.current_BP >= 1 or self.current_SYSSERVER >= 1:
                backup = open (self.filename, 'a')
                backup.write ('try:\n')
                backup.write ('    print rec_number\n')
                backup.write ('    pwd = os.getcwd()\n')
                backup.write ('    lsd = int(rec_number) % 10\n')
                backup.write ('    lsd_set = 1\n')
                backup.write ('except:\n')
                backup.write ('    print \'Looks like adding record was still not successfull try again later\'\n')
                backup.write ('    lsd_set = 0\n\n')
                backup.write ('if lsd_set == 1:\n')
                backup.write ('    crash_log_folder_lsd = os.path.join(pwd, \'CrashLogs\', str(lsd))')
                backup.write ('    if not os.path.exists(crash_log_folder_lsd):\n')
                backup.write ('        os.makedirs(crash_log_folder_lsd)\n')
                backup.write ('    log_time_app = \'' + self.log_time_app + '\'\n')
                backup.write ('    barcode = \'' + self.barcode + '\'\n')
                backup.write ('    fc = ' + str(self.current_FC) + '\n')
                backup.write ('    anr = ' + str(self.current_ANR) + '\n')
                backup.write ('    tomb = ' + str(self.current_Tomb) + '\n')
                backup.write ('    kernel = ' + str(self.current_Kernel) + '\n')
                backup.write ('    bp = ' + str(self.current_BP) + '\n')
                backup.write ('    ss = ' + str(self.current_SYSSERVER) + '\n')
                backup.write ('    blurver = \'' + self.blurver + '\'\n')
                backup.write ('    logcat_name = \'' + logcat_move + '\'\n')
                backup.write ('    anrtrace_name = \'' + anr_move + '\'\n')
                backup.write ('    temp_path = os.path.join(pwd,blurver)\n')
                backup.write ('    logcat_path = os.path.join(temp_path, logcat_name)\n')
                backup.write ('    anr_path = os.path.join(temp_path, anrtrace_name)\n')
                backup.write ('    crash_directory = crash_log_folder\n')
                backup.write ('    logcat_move = \'logcat_%s_%s_%s.txt\' % ( barcode, rec_number, log_time_app )\n')
                backup.write ('    anr_move = \'ANR_TRACES_%s_%s_%s.txt\' % ( barcode, rec_number, log_time_app )\n')
                backup.write ('    traces_move = os.path.join(crash_directory, anr_move)\n')
                backup.write ('    if fc >= 1 or anr >= 1 or tomb >= 1 or kernel >= 1 or bp >= 1 or ss >= 1:\n')
                backup.write ('        print \'Copying files from temp directory to where they should belong to have active links in the gadget\'\n')
                backup.write ('        shutil.copy2(logcat_path, os.path.join(crash_directory,logcat_move))\n')
                backup.write ('    if anr >= 1:\n')
                backup.write ('        shutil.copy2(anr_path, os.path.join(crash_directory, anr_move) )\n\n')
                backup.close ()'''

    def formatErr(self, err):
        exctype, value, tb = err
        return ''.join(traceback.format_exception(exctype, value, tb))
