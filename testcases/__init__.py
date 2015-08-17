
import cPickle
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time

import android

LOGS_PULLED_FILENAME = 'logsPulled.pkl'
TAG = os.path.basename(os.path.dirname(__file__)) + '/__init__.py'
lsSRE = re.compile("(.{1}).*([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}) (.*)")


def _copyLogs(connection, locations):
    logsPulledPath = os.path.join(android.log.report_directory(),
                                  LOGS_PULLED_FILENAME)
    if os.path.exists(logsPulledPath):
        try:
            logsPulledFile = open(logsPulledPath, 'rb')
            logsPulled = cPickle.load(logsPulledFile)
            logsPulledFile.close()
        except Exception, e:
            err = "logsPulled file opening or pickle loading failed. "
            err += "Exception: " + str(e)
            android.log.warning(TAG, err)
            logsPulled = []
    else:
        logsPulled = []

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
                _maybeCopyFile(connection, thing.path, thing.dateTimeString, devicelogsPath, logsPulled)

    try:
        # overwrite existing file
        logsPulledFile = open(logsPulledPath, 'wb')
        cPickle.dump(logsPulled, logsPulledFile, 2)
        logsPulledFile.close()
    except Exception, e:
        err = 'Failed to dump logsPulled list to file. Exception message: '
        android.log.warning(TAG, err + str(e))


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


def _maybeCopyFile(connection, path, dateTimeString, logsPath, logsPulledReference, copyIfPresent=False):
    _relativePath = path.lstrip('/')
    newDateTime = dateTimeString.replace(' ','_').replace('-','').replace(':','')
    timeStampedRelativePath = _relativePath + '.' + newDateTime + '.txt'
    localPath = os.path.join(logsPath, timeStampedRelativePath)
    if ((os.path.exists(localPath) or timeStampedRelativePath in logsPulledReference) and
        not copyIfPresent):
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
            if 'No such file or directory' in entry:
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
        things = [x.lstrip().rstrip() for x in output.rstrip().split('\n')]
        files = []
        return files, things
        #for thing in things:
        #    files.extend(_listTree(connection, thing))
        #return files
    output = connection.device.sh("ls -l " + _path)
    if output.find("No such file or directory") != -1:
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
        #if (android.settings.DEVICES['TestDevice']['id'] == connection.device.id() and not isConnecting):
        if not isConnecting:
            _copyLogs(connection, 
                      android.settings.LOCATIONS_PULLED_AFTER_EACH_TEST)
    except Exception, e:
        try:
            err = "managePhoneLogs(): Failure, with exception message: {0}."
            android.log.warning(TAG, err.format(str(e)))
        except:
            pass


android.register_connect_hook(managePhoneLogs)


@android.ui.waitfor_hook
def detect_force_close_and_anr_output_bugreport(a, s):
    #if a.device.id() != android.settings.DEVICES['TestDevice']['id']:
        #return False
    anr_fcs = []
    fc_regexp = re.compile(a.settings.UI_DETECT_FORCE_CLOSE_TEXT)
    anr_regexp = re.compile(a.settings.UI_DETECT_ANR_TEXT)
    if (    s.widget(id='message', text=fc_regexp) and
            s.widget(id='alertTitle') and
            s.widget(id='button1')):
        fname = 'bugreport_for_FC.txt'
        err_line1 = 'detect_force_close_output_bugreport(): '
        anr_fcs.append((fname, err_line1))
    if (    s.widget(id='message', text=anr_regexp) and
            s.widget(id='alertTitle') and
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

def productInitConnectionRecoveryHook(serialNumber):
    #if serialNumber != android.settings.DEVICES['TestDevice']['id']:
        #return
    devicelogsPath = (android.log.report_directory() + '/' + 
                      android.log.logs_directory() + '/devicelogs')

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
    for command, template in android.settings.LOG_ON_RUNTESTS_CONNECT:
        _command = ['adb', '-s', serialNumber, 'shell', command]
        try:
            fp = open(log_filename_no_connection(template, serialNumber), 'wb+')
        except Exception, e:
            err = ("Failed to open file with template {0} after reconnection, " + 
                   "with error '{1}'")
            android.log.warning(TAG, err.format(template, str(e)))
        try:
            popenNoApython(_command, stdout=fp)
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


android.register_connection_recovery_hook(productInitConnectionRecoveryHook)
