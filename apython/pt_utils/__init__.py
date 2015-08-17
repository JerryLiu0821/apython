"""This module copies logs from the test device.

Some logs are removed from the device after being copied; those needed for
automatic panic reporting by the device are left on it.

This module goes under the product folder for the device or 
handset being tested. If you are testing Kobe, for example, this module will
be Kobe/__init__.py

This module will need to change with changes in log locations. We get all 
logs at the locations indicated in:
http://wiki.mot-mobility.com/bin/view/IO/AndroidLogsLocations

Author: Brian Kyckelhahn
Earlier version by Suresh Nampalli
Enhancements made by Beylul Bahta
"""
import cPickle
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import datetime

import android

LOGS_PULLED_FILENAME = 'logsPulled.pkl'
TAG = os.path.basename(os.path.dirname(__file__)) + '/__init__.py'
lsSRE = re.compile("(.{1}).*([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}) (.*)")
#lsFileSRE = re.compile("([ldrwx-]{10}).* ([0-9]+)? ([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}) (.*)")
#
#TODO: use hashlib to create hash digest of fileName X fileSize
#
# import hashlib
# m = hashlib.md5()
# m.update( fileName )
# m.update( fileSize )
# m.hexdigest()
#

PHONE_FOLDER_REGEXP = re.compile( "Phone[0-9]" )

def findPhoneFolder( report_dir ):
    head, tail = os.path.split( report_dir )
    while( PHONE_FOLDER_REGEXP.search( tail ) == None ):
        if head == "": return report_dir
        head, tail = os.path.split( head )
    return os.path.join( head, tail )

def _moveLogs(connection, location):
    if not location:
        return

    filesAndFolders = runListTree(connection, location)
    if filesAndFolders:
        try:
            dateStr = sh( connection.internal.transport,
                          connection.internal.transport.adb_command,
                          "shell date",
                          log_level=connection.internal.settings.LOG_LEVEL_DEBUG)
            new_location = location + "_" + dateStr.replace(' ','_').replace('-','').replace(':','')
            sh(connection.internal.transport,
                connection.internal.transport.adb_command,
                "shell mv {src} {dest}".format(src=location, dest=new_location),
                log_level=connection.internal.settings.LOG_LEVEL_DEBUG)
            android.log.warning( TAG, "Successfully moved "+repr(location)+" on device" )
        except Exception:
            android.log.warning( TAG, "Unable to move "+repr(location)+" on device" )
            pass

def _copyLogs(connection, locations):
    def openPickleFile( path ):
        if os.path.exists( path ):
            try:
                logsPulledFile = open(path, 'rb' )
                logsPulled = cPickle.load( logsPulledFile )
                logsPulledFile.close()
            except Exception, e:
                err = "logsPulled file opening or pick loading failed. "
                err += "\nException: " + str( e )
                err += "\nPath: " + str( path )
                android.log.warning(TAG, err)
                logsPulled = []
        else:
            logsPulled = []
        return logsPulled

    def updatePickleFile( path, data ):
        try:
            logsPulledFile = open( path, 'wb' )
            cPickle.dump( data, logsPulledFile, 2 )
            logsPulledFile.close()
        except Exception, e:
            err = 'Failed to dump logsPulled list to file.'
            err += '\nException message: '+str(e)
            err += '\nPath: '+str( path )
            android.log.warning(TAG, err )

    logsPulledPath = os.path.join( android.log.report_directory(), LOGS_PULLED_FILENAME )
    parentPath = os.path.join( android.log.report_directory(), os.pardir )
    if PHONE_FOLDER_REGEXP.search( str( android.log.report_directory() )) !=None:
        globalLogsPulledPath = os.path.join( findPhoneFolder(parentPath), LOGS_PULLED_FILENAME )
    else:
        globalLogsPulledPath = os.path.join( parentPath, LOGS_PULLED_FILENAME )

#    print "LogsPulledPath: "+logsPulledPath
#    print "GlobalLogsPulledPath: "+globalLogsPulledPath

    globalLogsPulled = openPickleFile( globalLogsPulledPath )
    logsPulled = openPickleFile( logsPulledPath )

    devicelogsPath = (android.log.report_directory() + '/' + 
                      android.log.logs_directory() + '/devicelogs')
    if not os.path.exists(devicelogsPath):
        try:
            os.mkdir(devicelogsPath)
        except Exception, e:
            err = "Failed to create devicelogs directory. "
            err += "Exception message: " + str(e)
            android.log.warning(TAG, err)
            return

    for location in locations:
        filesAndFolders = runListTree(connection, location)
        for thing in filesAndFolders:
            if isinstance(thing, Folder):
                _makeLocalPath(thing.path, devicelogsPath)
            else:
                _maybeCopyFile(connection, thing.path, thing.dateTimeString, devicelogsPath, logsPulled, globalLogsPulled )


    globalLogsPulled += logsPulled
    updatePickleFile( globalLogsPulledPath, globalLogsPulled )
    updatePickleFile( logsPulledPath, logsPulled )

def _makeLocalPath(subPath, parentPath):
    relativeFolder = subPath.lstrip('/').rstrip('/')
    localFolderPath = os.path.join(parentPath, relativeFolder)
    for parentFolder in relativeFolder.split('/'):
        parentPath = os.path.join(parentPath, parentFolder)  
        if not os.path.exists(parentPath):
            try:
                os.mkdir(parentPath)
            except Exception, e:
                err = "Failed to make directory {0}, with error: {1}"
                android.log.warning(TAG, err.format(parentPath, str(e)))
                return


# If copyIfPresent=False, logs copied previously are not copied again, change this to True if you
# want the logs to be copied each time. (For example when using wildcards to pull multiple logs)
# Side effect: Setting this option will also pull tombstones etc...each and every time,this is
# not recommended.
def _maybeCopyFile(connection, path, dateTimeString, logsPath, logsPulledReference, globalLogsPulledReference, copyIfPresent=False):
    _relativePath = path.lstrip('/')
    newDateTime = dateTimeString.replace(' ','_').replace('-','').replace(':','')
    timeStampedRelativePath = _relativePath + '.' + newDateTime + '.txt'
    localPath = os.path.join(logsPath, timeStampedRelativePath)
    if ((os.path.exists(localPath) or 
          timeStampedRelativePath in logsPulledReference or
          timeStampedRelativePath in globalLogsPulledReference) and not copyIfPresent):
        # Two points:
        # 1. Chaitanya said not to worry about two tests running in the
        #    same minute (which would cause a problem because ls's resolution
        #    is only to the minute), because they won't run that fast.
        # 2. It may be a bug in the device, but I've seen files of the same 
        #    name in a directory on Android.
        return
    if os.path.exists(localPath):
        contents = os.listdir(os.path.dirname(localPath))
        basenamePrefix = os.path.basename(localPath)[:-len('.txt')]
        existing = [x for x in contents if x.startswith(basenamePrefix)]
        localPath = os.path.join(logsPath, (localPath[:-len('txt')] +
                                            str(len(existing) + 1) + '.txt'))

    internal_adb_hang_recovery_timeout = android.settings.INTERNAL_ADB_HANG_RECOVERY_TIMEOUT
    try:
        # Because we are calling adb pull, we use the custom
        # sh() procedure defined in this module.
        sh(connection.internal.transport,
           connection.internal.transport.adb_command,
           "pull {src} {dest}".format(src=path,
                                      dest=localPath),
           log_level=connection.internal.settings.LOG_LEVEL_DEBUG)
    except Exception:
        connection.internal.transport.internal.settings.INTERNAL_ADB_HANG_RECOVERY_TIMEOUT = android.settings.PRODUCT_INIT_EXTRA_LONG_ADB_HANG_RECOVERY_TIMEOUT
        try:
            sh(connection.internal.transport,
               connection.internal.transport.adb_command,
               "pull {src} {dest}".format(src=path,
                                          dest=localPath),
               log_level=connection.internal.settings.LOG_LEVEL_DEBUG)
        except Exception:
            android.log.debug(TAG, 'failed to pull: ' + path)
            connection.internal.transport.internal.settings.INTERNAL_ADB_HANG_RECOVERY_TIMEOUT = internal_adb_hang_recovery_timeout
            return
    finally:
        connection.internal.transport.internal.settings.INTERNAL_ADB_HANG_RECOVERY_TIMEOUT = internal_adb_hang_recovery_timeout 
        
    logsPulledReference += [timeStampedRelativePath]


class Folder(object):
    def __init__(self, path):
        self.path = path
    def __repr__(self):
        return self.path


class File(object):
    def __init__(self, path, dateTimeString):
        self.path = path
        self.dateTimeString = dateTimeString
    def __repr__(self):
        return self.path + '\t\t' + self.dateTimeString


def runListTree(connection, path):
    # Avoid recursion in _listTree().
    files, remainingEntries = _listTree(connection, path)
    while remainingEntries != []:
        newRemainingEntries = []
        for entry in remainingEntries:
            if 'No such file or directory' in entry or 'Permission denied' in entry:
                continue
            _files, _remainingEntries = _listTree(connection, entry)
            files += _files
            newRemainingEntries += _remainingEntries
        remainingEntries = newRemainingEntries
    return files


def _listTree(connection, path):
    # When called on a directory with contents, 'ls' returns the contents.
    # When called on an empty directory, 'ls' returns nothing.
    # When called on a file, 'ls' returns the filename.
    # When called on a shell glob, 'ls -l' returns the matching files and the
    # contents, but not the names, of the matching directories.
    _path = path.rstrip('/')
    if _path.find('*') != -1:
        output = connection.device.sh('ls -d ' + _path)
        if output.find("No such file or directory") > -1 or output.find("Permission denied") > -1:
            return [],[]
        things = [x.lstrip().rstrip() for x in output.rstrip().split('\n')]
        files = []
        return files, things
        #for thing in things:
        #    files.extend(_listTree(connection, thing))
        #return files
    output = connection.device.sh("ls -l " + _path)
    if output.find("No such file or directory") != -1 or output.find("Permission denied") > -1:
        # This is not an error. The log simply doesn't exist.
        return [], []
    things = [x.lstrip().rstrip() for x in output.rstrip().split('\n')]
    if things == ['']:
        # empty directory
        return [Folder(_path)], []

    if len(things) == 1:
        # file or directory with single entry
        match = lsSRE.search(things[0])
        if not match or len(match.groups()) != 3:
            return [], []
        _, dateTime, thingName = match.groups()
        _pathBase = os.path.basename(_path)
        if thingName == _pathBase:
            return [File(_path, dateTime)], []

    # directory with contents
    files = [Folder(_path)]
    directoriesToAdd = []
    for thing in things:
        match = lsSRE.search(thing)
        if not match or len(match.groups()) != 3:
            warning = "Strange failure to match ls output in line:" + thing
            android.log.warning(TAG, warning)
            return files, []
        thingType, dateTime, fileName = match.groups()
        if thingType == '-':
            files += [File(_path + '/' + fileName, dateTime)]
        elif thingType == 'd':
            directoriesToAdd += [_path + '/' + fileName]
    return files, directoriesToAdd
        #for aDir in directoriesToAdd:
        #    files.extend(_listTree(connection, _path + '/' + aDir))
        #return files, []

#def popen(self, adb_command, command, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
#    if isinstance(command,str): command = command.split()
#    return subprocess.Popen(adb_command + command, stdout=stdout, stderr=stderr,
#                            close_fds=isinstance(self, android.internal.transport_adb) and
#                            sys.platform not in [ 'win32', 'cygwin' ])
#
#

def kill_process(process):
    """ subprocess.Popen().kill() only exists in 2.6+ """
    if 'kill' in dir(process):
        try:
            process.kill()
        except:
            # On Windows, this throws an exception if the process has
            # already exited (for example, if the device was unplugged)
            pass
    else:
        # signal.SIGKILL is not defined in at least some versions of Python,
        # such as Python 2.6.5 on Windows XP, though it is used in apython.
        if hasattr(signal, 'SIGKILL'):
            os.kill(process.pid, signal.SIGKILL)
        else:
            os.kill(process.pid, signal.SIGINT) 


# popen has to be kept in this file, b/c that's the method that inserts 
# 'sh' in apython. The methods between sh() and popen() then have to be
# maintained here so that they call this version of popen, rather than
# then one in apython.
def popen(self, command, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    if isinstance(command,str): command = command.split()
    return subprocess.Popen(command,
            stdout=stdout, stderr=stderr,
            close_fds=    isinstance(self,android.internal.transport_adb) and
                        sys.platform not in [ 'win32', 'cygwin' ])

# This method could be left out, but we leave it here in case a change is
# made to it in apython and we overlook it.
def __connect_with_retry(self, action):
    if hasattr(self,'in_connect_with_retry'):
        # Avoid stacking retries. Only the topmost request is retried.
        return action()

    retries=self.internal.settings.INTERNAL_RETRY_ON_CONNECTION_ERROR_RETRIES if self.internal.settings.INTERNAL_RETRY_ON_CONNECTION_ERROR else 0
    assert retries >= 0

    self.in_connect_with_retry=True
    try:
        for retry in range(retries + 1):
            try:
                r=action()
                if retry > 0:
                    android.log.debug(TAG, 'INTERNAL_RETRY_ON_CONNECTION_ERROR: connection recovered')
                    for h in android._connection_recovery_hooks:
                        h(self.id)
                return r
            except Exception:
                # Python 2.5 and 3.x have different syntaxes for specifying
                # the exception value above, so fetch it manually below.
                e=sys.exc_info()[1]

                if (retry == retries or not getattr(e,'may_retry_on_connection_error',False)):
                    raise
                android.log.debug(TAG, 'INTERNAL_RETRY_ON_CONNECTION_ERROR: %s' % e.message.splitlines()[0])
                time.sleep(self.internal.settings.INTERNAL_RETRY_ON_CONNECTION_ERROR_DELAY)
        assert False, 'Unreachable'
    finally:
        del self.in_connect_with_retry


def sh(self, adb_command, command, log_level=android.settings.LOG_LEVEL_DEBUG):
    assert len(command) < 1024, 'Command exceeds 1024 characters (%s)' % repr(command)
    def action():
        _command = command.split() if isinstance(command,str) else command
        return __sh(self, adb_command + _command, log_level)
    return __connect_with_retry(self, action)


def __sh(self, command, log_level):
    if not self.internal.settings.INTERNAL_ADB_HANG_RECOVERY:
        o,e=popen(self, command).communicate()
    else:
        def timed_sh(command, timeout, message):
            p=popen(self, command)
            t=threading.Timer(timeout, lambda: kill_process(p))
            t.daemon = True
            t.start()
            o,e=p.communicate()
            if not t.isAlive():
                raise android.internal.AdbHangException(message)
            t.cancel()
            return o,e

        try:
            
            o,e=timed_sh(command, self.internal.settings.INTERNAL_ADB_HANG_RECOVERY_TIMEOUT, '')
        except android.internal.AdbHangException:
            android.log.warning(TAG, 'sh: adb hang detected. Restarting adbd. THIS SHOULD BE CONSIDERED A WORKAROUND ONLY. This usually suggests a bug in the device software.')
            message='Unable to restart adbd. Aborting.'
            o,e=timed_sh((command[:3] + ['shell', 'ps']), 5, message)
            kill_command = ('shell kill ' + [ p.split()[1] for p in o.splitlines()
                            if p != '' and p.split()[-1] == '/sbin/adbd' ][0]).split()
            timed_sh((command[:3] + kill_command), 5, message)
            time.sleep(self.internal.settings.
                    INTERNAL_ADB_HANG_RECOVERY_DELAY)
            o,e=timed_sh(command, self.internal.settings.
                            INTERNAL_ADB_HANG_RECOVERY_TIMEOUT,
                            'adb wedged. Aborting.')

    #if not self.internal.settings.APYTHON_LEGACY_ENCODING:
    #    o,e = o.decode('utf-8'), e.decode('utf-8')
    if e.startswith('error: '):
        raise android.internal.AdbException(e, self.id)
    if log_level != None:
        android.log._log(log_level, TAG, '%s returned %s' %
                (repr(command), repr(o)))
    return o

def terminatePostconLogcatLogs(connection, isConnecting):
    try:
        global log_on_connect
        serialNumber = android.settings.DEVICES['TestDevice']['id']
        if( serialNumber == connection.device.id() and not isConnecting ):
            for p in log_on_connect:
                kill_process(p)
            log_on_connect = []
    except Exception, e:
        try:
            err = "terminatePostConLogcatLogs(): Failure, with exception message: {0}."
            android.log.warning( TAG, err.format(str(e)))
        except:
            pass

adbStartsAsRoot = False
def enableAdbRoot(connection, isConnecting):
    global adbStartsAsRoot
    try:
        serialNumber = android.settings.DEVICES['TestDevice']['id']
        if( serialNumber == connection.device.id() and isConnecting ):
            tempCmd = 'adb -s %s shell getprop service.adb.root' % str(serialNumber)
            result = os.popen( tempCmd ).read().strip()
            if "1" not in result and not adbStartsAsRoot:
                tempCmd = 'adb -s %s root ' % str(serialNumber)
                cmdResult = os.popen( tempCmd ).read().strip()
                print cmdResult
                if "already running as root" in cmdResult:
                    adbStartsAsRoot = True
                else:
                    time.sleep( 20 )
    except Exception, e:
        try:
            err = "enableAdbRoot(): Failure, with exception message: {0}."
            android.log.warning( TAG, err.format(str(e)))
        except:
            pass

def managePhoneLogs(connection, isConnecting):
    if (not hasattr(android.settings, 'LOCATIONS_PULLED_AFTER_EACH_TEST') or
        not hasattr(android.settings, 'FILES_PULLED_ON_CONNECTION_RECOVERY')):
        print
        print "A settings file that defines LOCATIONS_PULLED_AFTER_EACH_TEST"
        print "and FILES_PULLED_ON_CONNECTION_RECOVERY must be provided."
        print "Exiting."
        print
        sys.exit(1)
    try:
        if (android.settings.DEVICES['TestDevice']['id'] == connection.device.id() and
            not isConnecting):
            _copyLogs(connection, 
                      android.settings.LOCATIONS_PULLED_AFTER_EACH_TEST)

            if (hasattr( android.settings, 'RAMDUMP_LOCATION' ) and
                android.settings.RAMDUMP_LOCATION):
                _moveLogs( connection, android.settings.RAMDUMP_LOCATION )
    except Exception, e:
        try:
            err = "managePhoneLogs(): Failure, with exception message: {0}."
            android.log.warning(TAG, err.format(str(e)))
        except:
            pass

#@android.ui.waitfor_hook
def detect_force_close_and_anr_output_bugreport(a, s):
    if a.device.id() != android.settings.DEVICES['TestDevice']['id']:
        return False
    anr_fcs = []
    fc_regexp = re.compile(a.settings.UI_DETECT_FORCE_CLOSE_TEXT)
    anr_regexp = re.compile(a.settings.UI_DETECT_ANR_TEXT)
    if (    s.widget(id='message', text=fc_regexp) and
            s.widget(id='button1')):
        
        fname = 'bugreport_for_FC.txt'
        err_line1 = 'detect_force_close_output_bugreport(): '
        anr_fcs.append((fname, err_line1))

    if (    s.widget(id='message', text=anr_regexp) and
            s.widget(id='button1')):
        fname = 'bugreport_for_ANR.txt'
        err_line1 = 'detect_force_close_output_bugreport(): '
        anr_fcs.append((fname, err_line1))
    if anr_fcs == []:    
        return False
    for failure in (anr_fcs):
        try:
            #o = sh(a.internal.transport,
            #       a.internal.transport.adb_command,
            #       "bugreport",
            #       log_level=None)
            o = a.device.sh('bugreport')
        except Exception, e:
            err = failure[1]
            err += "Failed to generate bugreport. Exception message: {0}."
            android.log.warning(TAG, err.format(str(e)))
            continue
        try:
            fp = open(a.log.log_filename(failure[0]), 'wb+')
            fp.write(o.encode('utf-8'))
            fp.close()
        except Exception, e:
            err = "Failed to write bugreport file. Exception message: {0}."
            android.log.warning(TAG, err.format(str(e)))
    return False

log_on_connect = []

def productInitConnectionRecoveryHook(serialNumber):
    if serialNumber != android.settings.DEVICES['TestDevice']['id']:
        return
    #this code is for getting the root access if the device powercycles in the middle of the test scripts
    tempvar = 'adb -s '+str(serialNumber)+' root'
    os.system (tempvar)
    time.sleep(20)
    
    devicelogsPath = (android.log.report_directory() + '/' + 
                      android.log.logs_directory() + '/devicelogsyyy')

    if not os.path.exists(devicelogsPath):
        try:
            os.mkdir(devicelogsPath)
        except Exception, e:
            err = "Failed to make devicelogs folder. Exception message: {0}."
            android.log.warning(TAG, err.format(str(e)))
            return
        
    for androidPath in android.settings.FILES_PULLED_ON_CONNECTION_RECOVERY:
        _makeLocalPath(os.path.dirname(androidPath), devicelogsPath)
        _pullFileNoApython(serialNumber, androidPath, devicelogsPath)

    def log_filename_no_connection(template, serialNumber):
        assert '.' in template
        prefix = template.rsplit('.', 1)[0] + '.postConRecovery.' + serialNumber
        logsPath = os.path.join(android.log.report_directory(), android.log.logs_directory())
        existing = [x for x in os.listdir(logsPath) if x.startswith(prefix)]
        f = os.path.join(android.log.logs_directory(),
                         (prefix + '.' + str(len(existing) + 1) + '.' +
                          template.rsplit('.', 1)[1]))
        path = os.path.join(android.log.report_directory(), f)
        try:
            os.mkdir(os.path.dirname(path))
        except OSError:
            pass

        type, format = template.rsplit('.',1)
        android.log.log_report(html=None,
                xml='        <%s format="%s" id="%s" src="%s" />\n' %
                        (type, format, serialNumber, f))
        return path

    androidConnection = None
    global log_on_connect

    for command, template in android.settings.LOG_ON_RUNTESTS_CONNECT:
        _command = ['adb', '-s', serialNumber, 'shell', command]
        try:
            fp = open(log_filename_no_connection(template, serialNumber), 'wb+')
        except Exception, e:
            err = ("Failed to open file with template {0} after reconnection, " + 
                   "with error '{1}'")
            android.log.warning(TAG, err.format(template, str(e)))
        try:
            log_on_connect.append( popenNoApython(_command, stdout=fp) )
        except Exception, e:
            err = ("Failed to begin logging with command {0} after " +
                   "reconnection, with error '{1}'")
            android.log.warning(TAG, err.format(_command, str(e)))


def _pullFileNoApython(serialNumber, androidPath, devicelogsPath):
    """This routine pulls files even when apython objects may not be
    fully instantiated, and therefore needs to be separate from _copyLogs().
    """
    command = "adb -s {0} shell ls -l {1}".format(serialNumber, 
                                                  androidPath)
    command = command.split()
    try:
        o = shNoApython(command, serialNumber, log_level=None)
    except Exception, e:
        err = ("Failed to call 'ls -l {path}' after possible reset, " + 
               "with error: {err}")
        err = err.format(path=androidPath, err=str(e))
        android.log.warning(TAG, err)
        return
    match = lsSRE.search(o.rstrip().split('\n')[0])
    fullLocalPath = os.path.join(devicelogsPath, androidPath.lstrip('/'))
    if not match or len(match.groups()) != 3:
        err = ("Unrecognized output from 'ls -l {path}'. " +  
               "Output: {output}.")
        err = err.format(path=fullLocalPath, output=o)
        android.log.warning(TAG, err)
        return
    _, dateTime, _ = match.groups()
    dateTime = dateTime.replace(' ','_').replace('-','').replace(':','')
    localDir = os.path.dirname(fullLocalPath)
    filename = os.path.basename(fullLocalPath)
    existing = [x for x in os.listdir(localDir) if
                x.startswith(filename + '.' + dateTime)]
    if existing != []:
        uniqueLocalPath = "{0}.{date}.{index}.txt".format(fullLocalPath,
                                                   date=dateTime,
                                                   index=str(len(existing) + 1))
    else:
        uniqueLocalPath = "{0}.{date}.txt".format(fullLocalPath, date=dateTime)
    command = "adb -s {id} pull {android} {local}"
    command = command.format(id=serialNumber, 
                             android=androidPath,
                             local=uniqueLocalPath).split()
    try:
        # XXX Use a second try with a longer timeout.
        o = shNoApython(command, serialNumber, log_level=None)
    except Exception, e:
        err = ("Failed to pull file {file} after possible reset, with " + 
               "error: {err}")
        err = err.format(file=filename, err=str(e))
        android.log.warning(TAG, err)


def shNoApython(command, serialNumber, log_level=android.settings.LOG_LEVEL_DEBUG):
    """Run command as passed with retry functionality.

    Despite its name, this routine does NOT prepend 'adb -s <serial number> shell'
    to command.format"""
    assert len(command) < 1024, 'Command exceeds 1024 characters (%s)' % repr(command)
    def action(): return __shNoApython(command, serialNumber, log_level)
    return __connect_with_retryNoApython(action, serialNumber)


def popenNoApython(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    if isinstance(command,str): command = command.split()
    return subprocess.Popen(command,
                            stdout=stdout, stderr=stderr,
                            close_fds=sys.platform not in [ 'win32', 'cygwin' ])


def __connect_with_retryNoApython(action, serialNumber, in_connect_with_retry=[]):
    if in_connect_with_retry != []:
        # Avoid stacking retries. Only the topmost request is retried.
        return action()

    retries=android.settings.INTERNAL_RETRY_ON_CONNECTION_ERROR_RETRIES if android.settings.INTERNAL_RETRY_ON_CONNECTION_ERROR else 0
    assert retries >= 0

    in_connect_with_retry=[True]
    try:
        for retry in range(retries + 1):
            try:
                r=action()
                if retry > 0:
                    android.log.debug(TAG, 'INTERNAL_RETRY_ON_CONNECTION_ERROR: connection recovered')
                    for h in android._connection_recovery_hooks:
                        h(serialNumber)
                return r
            except Exception:
                # Python 2.5 and 3.x have different syntaxes for specifying
                # the exception value above, so fetch it manually below.
                e=sys.exc_info()[1]

                if (retry == retries or not getattr(e,'may_retry_on_connection_error',False)):
                    raise
                android.log.debug(TAG, 'INTERNAL_RETRY_ON_CONNECTION_ERROR: %s' % e.message.splitlines()[0])
                time.sleep(android.settings.INTERNAL_RETRY_ON_CONNECTION_ERROR_DELAY)
        assert False, 'Unreachable'
    finally:
        in_connect_with_retry = []


def __shNoApython(command, serialNumber, log_level):
    if not android.settings.INTERNAL_ADB_HANG_RECOVERY:
        o,e = popenNoApython(command).communicate()
    else:
        def timed_sh(command, timeout, message):
            p=popenNoApython(command)
            t=threading.Timer(timeout, lambda: kill_process(p))
            t.daemon = True
            t.start()
            o,e=p.communicate()
            if not t.isAlive():
                raise android.internal.AdbHangException(message)
            t.cancel()
            return o,e

        try:
            o,e=timed_sh(command, android.settings.INTERNAL_ADB_HANG_RECOVERY_TIMEOUT, '')
        except android.internal.AdbHangException:
            android.log.warning(TAG, 'sh: adb hang detected. Restarting adbd. THIS SHOULD BE CONSIDERED A WORKAROUND ONLY. This usually suggests a bug in the device software.')
            message='Unable to restart adbd. Aborting.'
            o,e=timed_sh('adb -s {0} shell ps'.format(serialNumber), 5, message)
            timed_sh(('adb -s ' + str(serialNumber) + ' shell kill ' + 
                      [ p.split()[1] for p in o.splitlines() 
                       if p.split()[-1] == '/sbin/adbd' ][0]), 5, message)
            time.sleep(android.settings.
                       INTERNAL_ADB_HANG_RECOVERY_DELAY)
            o,e=timed_sh(command, android.settings.
                         INTERNAL_ADB_HANG_RECOVERY_TIMEOUT,
                         'adb wedged. Aborting.')

    #if not android.settings.APYTHON_LEGACY_ENCODING:
    #    o,e = o.decode('utf-8'), e.decode('utf-8')
    if e.startswith('error: '):
        raise android.internal.AdbException(e, serialNumber)
    if log_level != None:
        android.log._log(log_level, TAG, '%s returned %s' %
                (repr(command), repr(o)))
    return o

def __getAdditionalLogs(connection,path):
    serial_number = android.settings.DEVICES['TestDevice']['id']
    #Enable Tegra logcats
    subprocess.Popen('adb -s %s shell tegrastats' % (serial_number),shell = True)

    try:
        pid = subprocess.Popen('adb -s %s shell cat /proc/meminfo' % serial_number, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
        time.sleep(1)
        (std_out, error) = pid.communicate() 
        #pid.wait()
    except Exception, e:
        return 


    now = datetime.datetime.now()
    time_information = "%s_%s_%s_%s_%s_%s_" %(now.year,now.month,now.day,now.hour,now.minute,now.second)
    try:
        # Get meminfo
        meminfo_file =  "meminfo_%s" % str(time_information)
        filename = connection.log.log_filename(meminfo_file+str('.txt'))

        fh = open(filename,'a')
        fh.write("".join(std_out))
        fh.close()

    except Exception,e:
        print str(e)

    try:
        pid = subprocess.Popen('adb -s %s shell dumpsys SurfaceFlinger' % serial_number, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
        time.sleep(1)  
        (std_out, error) = pid.communicate() 
        #pid.wait()
    except Exception, e:
        return 

    now = datetime.datetime.now()
    time_information = "%s_%s_%s_%s_%s_%s_" %(now.year,now.month,now.day,now.hour,now.minute,now.second)

    try:
        # Get graphics info
        graphics_file =  "SurfaceFlinger_%s" % str(time_information)
        filename = connection.log.log_filename(graphics_file+str('.txt'))

        fh = open(filename,'a')
        fh.write("".join(std_out))
        fh.close() 

    except Exception,e:
        print str(e) 

#android.register_connect_hook(__getAdditionalLogs) 
android.register_connect_hook(enableAdbRoot)
android.register_connect_hook(managePhoneLogs)
android.register_connect_hook(terminatePostconLogcatLogs)
android.register_connection_recovery_hook(productInitConnectionRecoveryHook)

def determine_device_ip( device_barcode ):
    """
        Try to determine device ip address that matches provide device_barcode
    """
    ip_command = "ipconfig"
    if sys.platform != "win32" and sys.platform != "cygwin":    
        ip_command = "ifconfig"  
    co = subprocess.Popen( ip_command, stdout = subprocess.PIPE )
    output = co.stdout.read()
    ip_regex = re.compile('((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-4]|2[0-5][0-9]|[01]?[0-9][0-9]?))')
    addresses = [match[0] for match in ip_regex.findall( output, re.MULTILINE) if str(match[0]).startswith( "192.")]
    
    def verify_barcode_on_device( ipaddress, barcode, command ):
        """
            Verify that barocde provide matches on device with provide ipaddress
        """
        str = ""
        try:
            tn = telnetlib.Telnet( ipaddress )
            tn.read_until("#")
            tn.write( command+"\n" )
            tn.read_until( command )
            str = tn.read_until( "#" )
            tn.write( "exit\n" )
            tn.read_until( "#" )
            tn.close()
        except:
            android.log.debug(TAG,  "Unexpected error while attempting to verify barcode:" + repr( sys.exc_info()) )
            print "Unexpected error while attempting to verify barcode:", repr( sys.exc_info())
            pass
            
        print "Attempting to match barcode %s to string %s\n" % ( barcode, str )
        android.log.debug( TAG,"Attempting to match barcode %s to string %s\n" % ( barcode, str ) )        
        if str.find( barcode ) >= 0:
            print " found barcode "
            android.log.debug( TAG, "Found Barcode" )
            return True
        return False
    
    def update_ip_address( address ):
        ip_segments = str(address).split( "." )
        ip_segments[-1] = str( int(ip_segments[-1])+1 )
        return ".".join( ip_segments )
    
    serial_no_properties = [ 'getprop ro.serialno', 'getprop ro.ril.barcode', 'getprop ro.gsm.barcode']
    for address in addresses:
        ip_address = update_ip_address( address )
        print "Trying ip address: " + ip_address
        android.log.debug(TAG, "Trying ip address: " + ip_address )
        for command in serial_no_properties:
            if verify_barcode_on_device( ip_address, device_barcode, command ):
                return ip_address

def kill_adbd_on_device( device_barcode=None ):
    android.log.debug( TAG, "Callling kill_adbd_on_device " )
    if device_barcode is None:
        device_barcode = android.settings.DEVICES['TestDevice']['id']        
    ipaddress = determine_device_ip( device_barcode )
    if ipaddress is None:
        android.log.debug( TAG, "No device found with ip address that matches barcode: "+ device_barcode )
        return    
    tn = telnetlib.Telnet( ipaddress )
    tn.read_until( "#" )
    tn.write( "busybox killall adbd; exit\n" )
    str = tn.read_until( "#" )    
    tn.close()    
    print str
    android.log.debug( TAG, str )

#android.register_connection_failure_hook( "offline", kill_adbd_on_device )
