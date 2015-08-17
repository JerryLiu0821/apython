""" Glue module. Does not contain any public APIs. """

__all__ = [ 'StartViewServerException' ]

import android
import os, re, signal, socket, struct, subprocess, sys, threading, time, weakref

TAG='internal'

class StartViewServerException(Exception):
    def __init__(self, reason):
        Exception.__init__(self, 'Unable to start view server: ' + reason)
        self.may_retry_on_connection_error=True

class AdbException(Exception):
    def __init__(self, message, id):
        if message.startswith('error: more than one device and emulator'):
            message = (message.strip() + """

More than one connected Android device and/or emulator detected.
Please pass an id to android.connect() or use the --serial option of
runtests.py. Examples:

a1=android.connect(id='019617680601302D')
a2=android.connect(id='0196166B11033023')

or

python runtests.py --serial 019617680601302D mytest.py
""")
        else:
            message = '%s (id=%s)' % (message.strip(), id)
        Exception.__init__(self, message)
        self.may_retry_on_connection_error = message.startswith(
                ( 'error: device not found', 'error: device offline') )

class AdbHangException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class ViewServerNotRespondingException(Exception):
    VIEW_SERVER_NOT_RESPONDING_TEXT='View server not responding.'

    def __init__(self):
        Exception.__init__(self, self.VIEW_SERVER_NOT_RESPONDING_TEXT)

def kill_process(process):
    """ subprocess.Popen().kill() only exists in 2.6+ """
    if hasattr(process, 'kill'):
        try:
            process.kill()
        except:
            # On Windows, this throws an exception if the process has
            # already exited (for example, if the device was unplugged)
            pass
    else:
        os.kill(process.pid, signal.SIGKILL)

if sys.version[0] != '2':
    def decode(b,encoding='utf-8'): return b.decode(encoding)
    def encode(s,encoding='utf-8'): return s.encode(encoding)
else:
    def decode(b,encoding='utf-8'): return b
    def encode(s,encoding='utf-8'): return s

class adb:
    def __init__(self,id):
        self.id=id
        self.s=socket.socket()
        self.s.settimeout(5.0)
        self.s.connect(('127.0.0.1',5037))
        self.xfer('host:transport-any' if id is None else
                ('host:transport:%s' % id))

    def close(self):
        self.s.close()

    def xfer(self, command):
        self.s.sendall(encode('%04x%s' % (len(command), command)))
        result=decode(self.s.recv(4))
        if result == 'OKAY':
            return self
        if result == 'FAIL':
            raise AdbException('error: ' + decode(self.s.recv(
                    int(decode(self.s.recv(4)),16))), self.id)
        raise AdbException('FAIL: %s' % repr(result), self.id)

    def read(self,n):
        b=encode('')
        while len(b) < n:
            _ = self.s.recv(n-len(b))
            if len(_) is 0:
                self.s.close()
                break
            b += _
        return b

class transport_generic:
    def __init__(self,internal,id):
        if id is not None:
            raise Exception('Device id is only valid when running remotely')

        self.internal = internal
        self.sh_command = self.internal.settings.INTERNAL_SU_COMMAND.split()

    def __del__(self):        pass    # for debugging with gc.garbage

    def serial_number(self): return None

    def adb(self, command):
        raise Exception('adb commands can only be run from the PC')

    def screenshot(self):
        raise Exception('Screenshot cannot be taken during on-device execution')

    def popen(self, command, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
        if not isinstance(command,list): command = [ command ]
        return subprocess.Popen(self.sh_command + command,
                stdout=stdout, stderr=stderr,
                close_fds=    isinstance(self,android.internal.transport_adb) and
                            sys.platform not in [ 'win32', 'cygwin' ])

    def sh(self, command, input=None,
            log_level=android.settings.LOG_LEVEL_DEBUG):
        o,e=self.popen(command, stderr=subprocess.STDOUT).communicate(
                input=input)
        if log_level != None:
            android.log._log(log_level, TAG, '%s returned %s' %
                    (repr(command), repr(o)))
        return o.decode('utf-8')

    def start_view_server(self):
        for i in range(self.internal.settings.INTERNAL_VIEW_SERVER_START_RETRIES+1):
            o=self.sh('service call window 1 i32 4939')
            if re.match( # Returns 1 if starting, 0 if already started
                    r"Result: Parcel\(00000000 0000000[01]   '........'\)",o):
                return
            android.log.warning(TAG, 'Error starting view server: %s' % o)
            time.sleep(self.internal.settings.INTERNAL_VIEW_SERVER_START_RETRY_INTERVAL)
        raise StartViewServerException(o)

    def view_server_port(self):
        return 4939

    _BRIEF_VIEW_SERVER_COMMANDS=('CAPTURE ',)

    def view_server_generic(self, command, timeout, handler):
        TAG='internal.query'

        if timeout is None:
            timeout=self.internal.settings.INTERNAL_VIEW_SERVER_QUERY_DEFAULT_TIMEOUT

        retry_delay = self.internal.settings.INTERNAL_VIEW_SERVER_QUERY_RESTART_TIMEOUT
        for i in range(5):
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # Py3k raises an OverflowError on connect to port -1
                if self.view_server_port() == -1:
                    raise socket.error('Need to start port forwarding')
                s.connect(('127.0.0.1', self.view_server_port()))
                android.log.debug(TAG, 'Sending command: %s' % repr(command))
                s.sendall(encode(command))
                s.settimeout(timeout)
                data=encode('')

                t0 = time.time()
                while True:
                    datum=s.recv(32*1024)
                    android.log.verbose(TAG, 'Received %d bytes' % len(datum))
                    if datum == '': raise socket.error('Socket closed')

                    if len(data) < 256 or not command.startswith(
                            self._BRIEF_VIEW_SERVER_COMMANDS):
                        android.log.veryverbose(TAG, 'Received: %s'%repr(datum))

                    data+=datum

                    r=handler(command,data)
                    if r is not None:
                        return r

                    if time.time() - t0 > timeout:
                        raise socket.error('Timeout')
            except socket.error:
                def start_view_server():
                    try:
                        self.start_view_server()
                    except StartViewServerException:
                        android.log.warning(TAG,
                                'Error starting view server: %s. Ignored.' %
                                repr(sys.exc_info()))

                if not hasattr(self, 'view_server_started'):
                    android.log.info(TAG, 'Starting view server')
                    start_view_server()
                    time.sleep(1)
                    self.view_server_started=True
                    continue

                android.log.info(TAG,
"""Error (%s) with query: %s
THIS IS INFORMATIONAL ONLY AND IS NOT A PROBLEM UNLESS AN EXCEPTION IS RAISED.
Restarting view server and retrying query.""" %
                        (repr(sys.exc_info()[1]), repr(command)))

                # There are occasional spurious view server query failures
                # (this may be reproduced by sending many view server queries
                # in a row without delays in between); the following sleep
                # command gives the view server time to recover before retrying.
                time.sleep(retry_delay)

                # Exponential backoff
                retry_delay *= 2
                if retry_delay > 5:
                    retry_delay = 5

                # If there has been a framework reset, the forwarding socket
                # remains connect()able, but is closed immediately upon a
                # write. The next line restarts the view server to handle
                # this case.
                start_view_server()

            finally:
                android.log.debug(TAG, 'Closing socket.')
                s.close()

        if self.internal.settings.EXPERIMENTAL_INTERNAL_KILL_UNRESPONSIVE_VIEW_SERVER:
            android.log.info(TAG,
                    'View server not responding. Killing view server thread')
            self.sh('service call window 2')
            time.sleep(3)
        raise ViewServerNotRespondingException()

        _n = encode('\n')
    _nDONEn, _DONEn = encode('\nDONE.\n'), encode('DONE.\n')
    _nDONEnDONEn, _DONEnDONEn = encode('\nDONE.\nDONE\n'), encode('DONE.\nDONE\n')

    def view_server_query(self, command, timeout=None):
        def handler(command, data):
            if data.endswith(self._nDONEn):
                return data.decode('utf-8').split('\n')[:-2]
            # Termination string on some builds
            if data.endswith(self._nDONEnDONEn):
                return data.decode('utf-8').split('\n')[:-3]
            if data in [ self._DONEn, self._DONEnDONEn ]:
                return []
            if "GET_FOCUS" in command and data.endswith(self._n):
                                return data.decode('utf-8').split('\n')[:-1]

            return None
        return self.view_server_generic(command, timeout, handler)

    def view_server_capture(self, window_hash, view_type, view_hash):
        PNG=encode('\x89\x50\x4E\x47\x0D\x0A\x1A\x0A', 'iso-8859-1')
        IEND=encode('IEND')
        def handler(command, data):
            if len(data) > 8:
                if data[:8] != PNG:
                    raise Exception('Unexpected header: %s' % repr(data[:8]))
                off=8
                while len(data) >= off + 8:
                    chunklen,tag=struct.unpack_from('>I4s', data, off)
                    off+=chunklen+12
                    if len(data) == off and tag == IEND:
                        return data
            return None

        return self.view_server_generic(
                'CAPTURE %s %s@%s\n' % (window_hash, view_type, view_hash),
                timeout=None, handler=handler)

    def sendevents(self, args):
        """ Send events as a batch. This speeds the posting of events, helping
            reduce the chance of a short press being misinterpreted as a long
            press. """
        assert len(args) > 0 and len(args) % 4 == 0
        while args:
            # Chunk to avoid exceeding the maximum command line length (1024):
            # 1024/len('sendevent /dev/input/event0 000 000 000;') == 25
            self.sh(''.join( [ 'sendevent %s %s %s %s;' % tuple(args[n:n+4])
                                    for n in range(0,min(len(args),100),4) ]))
            args=args[100:]

class transport_adb(transport_generic):

    ADB_COMMAND=None

    def __init__(self,internal,id):
        transport_generic.__init__(self,internal,None)

        if transport_adb.ADB_COMMAND is None:
            # Auto-detect adb command in PATH and ANDROID_HOME
            exe = [ 'adb', 'adb-win', 'adb-mac' ]
            search = [] + exe
            if 'ANDROID_HOME' in os.environ:
                search += [ os.path.join(os.environ['ANDROID_HOME'], 'tools',
                                        dir) for dir in exe ]
                                search += [ os.path.join(os.environ['ANDROID_HOME'], 'platform-tools',
                                                                                dir) for dir in exe ]
            for command in search:
                try:
                    # Run 'adb devices' to make sure the server is running so
                    # there is no unexpected output in future adb connections.
                    # Because adb spawns a background task, we can't use
                    # communicate(), which blocks on Windows until the
                    # background task exits.
                    subprocess.Popen( [ command, 'devices' ], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT).stdout.read(1)
                    transport_adb.ADB_COMMAND = command
                    break
                except OSError:
                    pass
        if transport_adb.ADB_COMMAND is None:
            raise Exception("Unable to execute 'adb', 'adb-mac', or 'adb-win': is adb installed?")

        id=id or os.environ.get('ANDROID_SERIAL')
        if id is None:
            id=decode(self.adb_raw('host:get-serialno').read(256))
            if int(id[:4],16) != len(id[4:]):
                raise Exception('Error retrieving serial number from adbd')
            id=id[4:]
            if len(id) == 0:
                raise Exception('Invalid serial number for device: (empty)')
            android.log.info(TAG, "Connecting to serial number: '%s'" % id)

        self.id=id
        self.port = -1
        self.adb_command = [ transport_adb.ADB_COMMAND, '-s', self.id ]
        self.sh_command = self.adb_command + [ 'shell' ]

    def __del__(self):        pass    # for debugging with gc.garbage

    def serial_number(self): return self.id

    def adb(self, command, input=None):
        if not isinstance(command,list): command=command.split()
        return subprocess.Popen( self.adb_command + command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT).communicate(input=input)[0]
    
    def runshell(self,cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        return p.communicate()[0]
    
    def adb_raw(self, command):
        id=getattr(self,'id',None)    # __init__() may call us to find the id
        def action(): 
            self.runshell([transport_adb.ADB_COMMAND, 'disconnect', id])
            self.runshell([transport_adb.ADB_COMMAND, 'connect', id])
            time.sleep(1)
            return android.internal.adb(id).xfer(command)
        return self.__connect_with_retry(action)

    def screenshot(self): return self.adb_raw('framebuffer:')

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

                    if (retry == retries or not getattr(
                            e,'may_retry_on_connection_error',False)):
                                                print "Retrying connection"
                                                for type, callback in android._connection_failure_hooks:
                                                        if str(e).find( type ) >= 0:
                                                                callback()
                        raise
                    android.log.debug(TAG, 'INTERNAL_RETRY_ON_CONNECTION_ERROR: %s' % str(e).splitlines()[0])
                    time.sleep(self.internal.settings.INTERNAL_RETRY_ON_CONNECTION_ERROR_DELAY)
            assert False, 'Unreachable'
        finally:
            del self.in_connect_with_retry

    def sh(self, command, input=input, log_level=android.settings.LOG_LEVEL_DEBUG):
        assert len(command) < 1024, 'Command exceeds 1024 characters (%s)' % repr(command)

        def action(): return self.__sh(command, input, log_level)
        return self.__connect_with_retry(action)

    def __sh(self, command, input, log_level):
        if not self.internal.settings.INTERNAL_ADB_HANG_RECOVERY:
            o,e=self.popen(command).communicate(input=input)
        else:
            def timed_sh(command, timeout, message):
                p=self.popen(command)
                t=threading.Timer(timeout, lambda: kill_process(p))
                t.daemon = True
                t.start()
                o,e=p.communicate(input=input)
                if not t.isAlive():
                    raise AdbHangException(message)
                t.cancel()
                return o,e

            try:
                o,e=timed_sh(command, self.internal.settings.INTERNAL_ADB_HANG_RECOVERY_TIMEOUT, '')
            except AdbHangException:
                android.log.warning(TAG, 'sh: adb hang detected. Restarting adbd. THIS SHOULD BE CONSIDERED A WORKAROUND ONLY. This usually suggests a bug in the device software.')
                message='Unable to restart adbd. Aborting.'
                o,e=timed_sh('ps', 5, message)
                timed_sh('kill ' + [ p.split()[1] for p in o.splitlines()
                        if p.split()[-1] == '/sbin/adbd' ][0], 5, message)
                time.sleep(self.internal.settings.
                        INTERNAL_ADB_HANG_RECOVERY_DELAY)
                o,e=timed_sh(command, self.internal.settings.
                                INTERNAL_ADB_HANG_RECOVERY_TIMEOUT,
                                'adb wedged. Aborting.')

        o,e = o.decode('utf-8'), e.decode('utf-8')
        if e.startswith('error: '):
            raise AdbException(e, self.id)
        if log_level != None:
            android.log._log(log_level, TAG, '%s returned %s' %
                    (repr(command), repr(o)))
        return o

    port_registry={}

    def start_view_server(self):
        transport_generic.start_view_server(self)

        """
        This chunk of code arbitrates ports between different instances of
        apython. This is necessary so that different instances of apython
        don't map the view server of two different devices to the same local
        port.

        It uses the simple convention of using sequential port numbers to
        specify the view server port and a listener port. Trying to bind to
        a used listener port will fail, letting apython know that port pair
        is already in use.
        """
        if self.id not in transport_adb.port_registry:
            for p in self.internal.settings.INTERNAL_VIEW_SERVER_PORT_RANGE:
                try:
                    android.log.debug(TAG, 'Probing port: %d' % p)

                    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.bind(('127.0.0.1',p))

                    transport_adb.port_registry[self.id] = (p+1,s)
                    break
                except socket.error:
                    pass
            else:
                raise Exception('No open ports found')

        self.port,self.s=transport_adb.port_registry[self.id]
        android.log.info(TAG, 'Found port: %d' % self.port)

        self.adb('forward tcp:%d tcp:4939' % self.port)

    def view_server_port(self):
        return self.port

    def view_server_generic(self, command, timeout, handler):
        def action(): return transport_generic.view_server_generic(
                        self, command, timeout, handler)
        return self.__connect_with_retry(action)

android_keymap={
    'SOFT_LEFT':'1', 'SOFT_RIGHT':'2', 'HOME':'3', 'BACK':'4','CHANNEL_UP':'166','CHANNEL_DOWN':'167',
    'CALL':'5', 'ENDCALL':'6', '0':'7', '1':'8', '2':'9', '3':'10',
    '4':'11', '5':'12', '6':'13', '7':'14', '8':'15', '9':'16',
    'STAR':'17', 'POUND':'18', 'DPAD_UP':'19', 'DPAD_DOWN':'20',
    'DPAD_LEFT':'21', 'DPAD_RIGHT':'22', 'DPAD_CENTER':'23',
    'VOLUME_UP':'24', 'VOLUME_DOWN':'25', 'POWER':'26', 'CAMERA':'27',
    'CLEAR':'28', 'A':'29', 'B':'30', 'C':'31', 'D':'32', 'E':'33',
    'F':'34', 'G':'35', 'H':'36', 'I':'37', 'J':'38', 'K':'39',
    'L':'40', 'M':'41', 'N':'42', 'O':'43', 'P':'44', 'Q':'45',
    'R':'46', 'S':'47', 'T':'48', 'U':'49', 'V':'50', 'W':'51',
    'X':'52', 'Y':'53', 'Z':'54', 'COMMA':'55', 'PERIOD':'56',
    'ALT_LEFT':'57', 'ALT_RIGHT':'58', 'SHIFT_LEFT':'59',
    'SHIFT_RIGHT':'60', 'TAB':'61', 'SPACE':'62', 'SYM':'63',
    'EXPLORER':'64', 'ENVELOPE':'65', 'ENTER':'66', 'DEL':'67',
    'GRAVE':'68', 'MINUS':'69', 'EQUALS':'70', 'LEFT_BRACKET':'71',
    'RIGHT_BRACKET':'72', 'BACKSLASH':'73', 'SEMICOLON':'74',
    'APOSTROPHE':'75', 'SLASH':'76', 'AT':'77', 'NUM':'78',
    'HEADSETHOOK':'79', 'FOCUS':'80', 'PLUS':'81', 'MENU':'82',
    'NOTIFICATION':'83', 'SEARCH':'84', 'MEDIA_PLAY_PAUSE':'85',
    'MEDIA_STOP':'86', 'MEDIA_NEXT':'87', 'MEDIA_PREVIOUS':'88',
    'MEDIA_REWIND':'89', 'MEDIA_FAST_FORWARD':'90', 'MUTE':'91'
}

class track_device:
    def __init__(self, internal, touch_dev, d, key_required=False, dev_name=None):
        self.internal=internal
        self.touch_dev=touch_dev
        self.d=d
        self.key_required=key_required
                self.dev_name=dev_name

    def _event(self, x, y, pressure):
        event=[]
                if '002f' in self.d: event += [ self.touch_dev, 3, 0x2f, 0 ] # if ABS_MT_SLOT defined
        if '0039' in self.d: event += [ self.touch_dev, 3, 0x39, 0 ]
        if '003a' in self.d: event += [ self.touch_dev, 3, 0x3a, pressure ]
        if '0032' in self.d: event += [ self.touch_dev, 3, 0x32, 6 ]
                if '0030' in self.d: event += [ self.touch_dev, 3, 0x30, 48 if '003a' in self.d else pressure ]
        event += [    self.touch_dev, 3, 0x35, x,
                    self.touch_dev, 3, 0x36, y ]

        if '0018' in self.d: event += [ self.touch_dev, 3, 0x18, pressure ]
        if self.key_required: event += [ self.touch_dev, 1, 0x14a, 0 if pressure == 0 else 1 ]

                event += ([    self.touch_dev, 0, 2, 0 ] if ( '002f' not in self.d ) else [])
        event += [    self.touch_dev, 0, 0, 0 ]
                return event

    def down(self, x, y):
        return self._event(x, y, 48)

    def up(self, x, y):
        return self._event(x, y, 0) + (
                [    self.touch_dev, 0, 2, 0,
                    self.touch_dev, 0, 0, 0 ] if (('003a' in self.d and '002f' not in self.d ) or
                            self.internal.settings.INTERNAL_TOUCH_REQUIRES_DOUBLE_SYNC)
                                                        else [] ) + (
                                [       self.touch_dev, 3, 0x2f, -1,
                                        self.touch_dev, 0, 0, 0 ] if ( '002f' in self.d ) else [])

    def move(self, x, y):
        return self.down(x, y)

    def touch(self, x, y):
        return self.down(x,y) + self.up(x,y)

class qt602240touch_device (track_device):
    def _event(self, x, y, pressure):
        event=[]
        if '003a' in self.d: event += [ self.touch_dev, 3, 0x3a, pressure ]
        if pressure > 0:
            if '0030' in self.d: event += [ self.touch_dev, 3, 0x30, 48 if '003a' in self.d else pressure ]
            event += [      self.touch_dev, 3, 0x35, x,
                            self.touch_dev, 3, 0x36, y ]

        event += ([     self.touch_dev, 0, 2, 0 ] if ( '002f' not in self.d ) else [])
        event += ([     self.touch_dev, 0, 2, 0 ] if ( '002f' not in self.d ) else [])
        event += ([     self.touch_dev, 0, 2, 0 ] if ( '002f' not in self.d ) else [])
        event += ([     self.touch_dev, 0, 2, 0 ] if ( '002f' not in self.d ) else [])
        event += ([     self.touch_dev, 0, 2, 0 ] if ( '002f' not in self.d ) else [])
        event += [      self.touch_dev, 0, 0, 0 ]
        return event

class touch_device:
    def __init__(self, touch_dev): self.touch_dev = touch_dev

    def _event(self, x, y, pressure): return [
            self.touch_dev, 3, 0, x,
            self.touch_dev, 3, 1, y,
            self.touch_dev, 1, 330, pressure,
            self.touch_dev, 0, 0, 0 ]

    def down(self, x, y): return self._event(x,y,1)
    def up(self, x, y): return self._event(x,y,0)
    def move(self, x, y): return [
            self.touch_dev, 3, 0, x,
            self.touch_dev, 3, 1, y,
            self.touch_dev, 0, 0, 0 ]
    def touch(self, x, y): return self.down(x,y) + [
            self.touch_dev, 1, 330, 0,
            self.touch_dev, 0, 0, 0 ]

class generic_device:
    def __init__(self, internal):
        self.internal=internal
        self.keymap={}
        self.height, self.width = 0, 0

        for o in re.compile(
                # For on device execution lines terminate with \n
                # For execution through adb shell, lines terminate with \r\n
                r'^add device .*\r?\n(?: .*\r?\n)+',re.MULTILINE).findall(
                internal.transport.sh('getevent -v 0xff -S')):
            android.log.veryverbose(TAG, 'parsing: ' + o)
            dev, name = re.match(r'add device \d+: (\S+)(?:.*\r?\n)+?\s+name:\s+"(.*?)"',o).groups()
            android.log.info(TAG, 'parsing: ' + name)

            has_014a = False

            # parse each event type block separately
            for _type, _params in re.compile(
                    # '    type 0000: 0000  0001  0003 '    # cupcake
                    # '    SYN (0000): 0000  0003 '            # donut+
                    r'^    (?:....? \(?([\da-f]{4})\)?): (.*\r?\n(?:     .*\r?\n)*)',
                    re.MULTILINE).findall(o):
                if _type == '0001':        # KEY
                    android.log.info(TAG, 'key device: ' + dev)

                    def cat(file):
                        output = internal.transport.sh('cat "%s"' % file)
                                                # limit regular expression searching to first 500 chars 
                        return None if re.search(r'%s: (No such file or directory|invalid length)[\r\n]' % file, output[:500]) else output

                    kl=cat('/system/usr/keylayout/%s.kl' % name)
                    if kl is None:
                        kl=cat('/system/usr/keylayout/qwerty.kl')

                    if kl is None:
                        android.log.warning(TAG,
                                'Unable to get keylayout for %s' % name)
                        continue

                    dev_keymap=dict()
                    for k in kl.splitlines():
                        if k.startswith('key'):
                            key = k.split()
                            dev_keymap['%04x' % int(key[1])] = (key[2], key[3] if len(key) > 3 else None)
                    android.log.debug(TAG, 'keys for %s' % name)
                    for keycode in _params.split():
                        if keycode == '014a': has_014a = True

                        if keycode not in dev_keymap: continue
                        keyname, keyflags = dev_keymap[keycode]
                        # WAKEUP keys take precedence
                        if keyname in self.keymap and keyflags is None:
                            continue

#                                                if keyname in { "HOME", "MENU", "BACK", "SEARCH" }:
#                                                        continue

                        self.keymap[keyname] = (dev, int(keycode,16))
                        android.log.debug(TAG, '  ' + keyname)

                elif _type == '0003':            # ABS
                    if hasattr(self, 'touch_dev'): continue

                    d=dict([ (_.groupdict()['type'], _.groupdict()) for _ in re.compile(r'(?P<type>[\da-f]{4})  (?:[: ]+)?value -?\d+, min (?P<min>-?\d+), max (?P<max>-?\d+), fuzz -?\d+,? flat -?\d+(?:, resolution \d+)?[\r\n]+', re.MULTILINE).finditer(_params) ])

                    if '0035' in d and '0036' in d:
                        x,y=d['0035'],d['0036']
                                            if "qt602240touch" in name:
                                                self.touch_dev=qt602240touch_device(self.internal, dev, d, has_014a, name )
                                            else:
                            self.touch_dev=track_device(self.internal, dev, d, has_014a, name)
                    elif '0000' in d and '0001' in d and has_014a:
                        # touch devices report ABS/000{0,1} and KEY/014a.
                        # some non-touch devices report ABS/000{0,1} but not
                        # KEY/014a
                        x,y=d['0000'],d['0001']
                        self.touch_dev=touch_device(dev)
                    else:
                        continue

                    android.log.info(TAG, 'touch device: %s (%s)' % (dev, name))

                    self.x_range = [ int(x['min']), int(x['max']) ]
                    self.y_range = [ int(y['min']), int(y['max']) ]

                    android.log.debug(TAG, 'touch screen ranges: x=%s, y=%s' %
                            (self.x_range, self.y_range))

                elif _type == '0005':            # SW
                    if '0000' in _params:
                        android.log.info(TAG, 'lid device: ' + dev)
                        self.flip_dev = dev

    def __del__(self):        pass    # for debugging with gc.garbage

    def set_lid(self,open):
        """ Caller MUST resniff orientation after calling this method. """
        if not hasattr(self, 'flip_dev'):
            raise Exception('set_lid: Could not find lid device')
        self.internal.transport.sendevents( [
                self.flip_dev, 5, 0, 0 if open else 1 ] )

    def text(self, arg):
        # Chunk text to avoid exceeding the maximum command line length
        # (1024 characters)
        n=self.internal.settings.INPUT_TEXT_CHUNK_SIZE
        while arg != '':
            arglet=arg[:n]
            self.internal.transport.sh('CLASSPATH=/system/framework/input.jar app_process /system/bin com.android.commands.input.Input text "%s"' %
                    re.sub(r'([\\"$])', r'\\\1', arglet))
            time.sleep(    min(self.internal.settings.INPUT_TEXT_DELAY_MAX,
                        max(self.internal.settings.INPUT_TEXT_DELAY_MIN,
                        self.internal.settings.INPUT_TEXT_DELAY(len(arglet)))))
            arg=arg[n:]

    def physical_keys(self):
        return self.keymap.keys()

    def key(self, k):
        if (    #k not in self.keymap and
                 self.internal.settings.INPUT_EMULATE_MISSING_KEYS):
                self.internal.transport.sh('input keyevent %s' % android_keymap[k])
           else:
            dev, keycode = self.keymap[k]
            self.internal.transport.sendevents( [
                    dev, 1, keycode, 1,
                    dev, 0, 0, 0,
                    dev, 1, keycode, 0,
                    dev, 0, 0, 0 ] )
        time.sleep(self.internal.settings.INPUT_KEY_UP_DELAY)

    def key_down(self, k):
        dev, keycode = self.keymap[k]
        self.internal.transport.sendevents( [
                dev, 1, keycode, 1,
                dev, 0, 0, 0 ] )
        time.sleep(self.internal.settings.INPUT_KEY_DOWN_DELAY)

    def key_up(self, k):
        dev, keycode = self.keymap[k]
        self.internal.transport.sendevents( [
                dev, 1, keycode, 0,
                dev, 0, 0, 0 ] )
        time.sleep(self.internal.settings.INPUT_KEY_UP_DELAY)

    def __translate(self, x, y):
        h,w=self.height,self.width
        x_range, y_range = self.x_range, self.y_range

        # FroYo emulator reports this
        if self.x_range == [ 0, 0 ]:
            x_range[1], y_range[1] = (w,h) if self.rotation & 1 == 0 else (h,w)

        if self.rotation == 0:
            return (x * (x_range[1] - x_range[0]) / w + x_range[0],
                    y * (y_range[1] - y_range[0]) / h + y_range[0])
        elif self.rotation == 1:
            return ((h - y) * (x_range[1] - x_range[0]) / h + x_range[0],
                    x * (y_range[1] - y_range[0]) / w + y_range[0])
        elif self.rotation == 2:
            return ((w - x) * (x_range[1] - x_range[0]) / w + x_range[0],
                    (h - y) * (y_range[1] - y_range[0]) / h + y_range[0])
        elif self.rotation == 3:
            return (y * (x_range[1] - x_range[0]) / h + x_range[0],
                    (w - x) * (y_range[1] - y_range[0]) / w + y_range[0])

        raise Exception('Unexpected rotation: ' + str(self.rotation))

    def touch_down(self, x, y):
        x,y = self.__translate(x,y)
        self.internal.transport.sendevents(self.touch_dev.down(x, y))
        time.sleep(self.internal.settings.INPUT_TOUCH_DOWN_DELAY)

    def touch_up(self, x, y):
        x,y = self.__translate(x,y)
        self.internal.transport.sendevents(self.touch_dev.up(x, y))
        time.sleep(self.internal.settings.INPUT_TOUCH_UP_DELAY)

    def touch_move(self, x, y):
        x,y = self.__translate(x,y)
        self.internal.transport.sendevents(self.touch_dev.move(x, y))
        time.sleep(self.internal.settings.INPUT_TOUCH_DOWN_DELAY)

    def touch(self, x, y):
        x,y = self.__translate(x,y)
        self.internal.transport.sendevents(self.touch_dev.touch(x, y))
        time.sleep(self.internal.settings.INPUT_TOUCH_UP_DELAY)

    def drag(self, x1, y1, x2, y2, steps, skip_down, skip_up, drag_delay):
        e=[]
        if not skip_down:
            x,y=self.__translate(x1,y1)
            e += self.touch_dev.down(x,y)
        for i in range(1, steps+1):
            x,y=self.__translate(x1+(x2-x1)*i/steps, y1+(y2-y1)*i/steps)
            e += self.touch_dev.move(x,y)
        self.internal.transport.sendevents(e)
        time.sleep(drag_delay if drag_delay is not None else
                self.internal.settings.UI_DRAG_DELAY)
        if not skip_up:
            self.touch_up(x2,y2)

class Internal:
    def __init__(self_,id,settings):
        self=weakref.proxy(self_) # avoid circular references in children

        self.settings = settings

        local = os.access('/default.prop', os.F_OK)
        self.transport=(transport_generic if local else transport_adb)(self,id)
        self.device=generic_device(self)

    def __del__(self):        pass    # for debugging with gc.garbage

module_callbacks = [ ]
def register_module_callback(callback):
    module_callbacks.append(callback)

class connect:
    def __init__(self_,id,settings):
        self=weakref.proxy(self_) # avoid circular references in children

        self.settings = android.settings.Settings(settings)
        self.internal = Internal(id,self.settings)

        for c in module_callbacks:
            c(self)

    def __del__(self):        pass    # for debugging with gc.garbage
