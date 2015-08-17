

import android, binascii, csv, os, re, socket, struct, sys, time
try:
	from StringIO import StringIO as BytesIO
except ImportError:
	from io import BytesIO		# Py3K

TAG='STABILITY'

decode=android.internal.decode
encode=android.internal.encode

def redoc(doc, s):
	if not doc: return s
	m=re.search('(\n\s+)', doc)	# keep the same indent to preserve formatting
	return doc + (m.group(1) if m else '\n') + s

def hook(c,fname=None):
	def decorator(f):
		name=f.__name__ if fname is None else fname
		doc=getattr(getattr(c, name), '__doc__') or ''
		setattr(f, '__doc__', redoc(doc,'(LV only enhanced)'))
		setattr(f, 'previous', getattr(c, name))
		setattr(c, name, f)
		return f
	return decorator

def add_api(c):
	def decorator(f):
		setattr(f, '__doc__', redoc(f.__doc__, '(LV only API)'))
		setattr(c, f.__name__, f)
		return f
	return decorator

android.ui.LOCK_SCREEN_WIDGETSPECS += [
		android.ui.widgetspec(type='com.huelabs.rdge.view.elements.RDGEScene',
				id='rdgeSceneRoot') ]

# XXX: make isChecked public for all devices?
android.ui.WIDGETSPEC_ATTRIBUTES += [ 'isChecked', 'drawables' ]

android.internal.ViewServerNotRespondingException.VIEW_SERVER_NOT_RESPONDING_TEXT="""View server not responding."""

def screenshot_base(self, previous):
	""" Unlike the default implementation, this version works both
		on user builds and during on device execution. """
	if self.internal.device.google_experience or not getattr(
			self.internal.settings, 'LV_USE_FRAMEBUFFER_COMMAND', False):
		return previous(self)

	return BytesIO(binascii.a2b_hex(''.join(
			self.internal.transport.view_server_query('FRAMEBUFFER\n',
					2*self.internal.settings.INTERNAL_VIEW_SERVER_QUERY_DEFAULT_TIMEOUT))))

@hook(android.internal.transport_adb, 'screenshot')
def screenshot_adb(self):
	return screenshot_base(self, screenshot_adb.previous)





@hook(android.internal.generic_device)
def key_down(self, k):
	if (	k in self.keymap or
			not self.internal.settings.INPUT_EMULATE_MISSING_KEYS or
			getattr(self.internal.settings, 'LV_AVOID_INPUT_COMMAND',
					self.internal.device.google_experience)):
		return key_down.previous(self, k)
	self.internal.transport.view_server_query(
			'INPUT KEYDOWN %s\n' % android.internal.android_keymap[k])

@hook(android.internal.generic_device)
def key_up(self, k):
	if (	k in self.keymap or
			not self.internal.settings.INPUT_EMULATE_MISSING_KEYS or
			getattr(self.internal.settings, 'LV_AVOID_INPUT_COMMAND',
					self.internal.device.google_experience)):
		return key_up.previous(self, k)
	self.internal.transport.view_server_query(
			'INPUT KEYUP %s\n' % android.internal.android_keymap[k])

@hook(android.input.Input)
def text(self, arg, delay=None):
    if not self.android.device.has_input_command_with_delay_option():
        return text.previous(self, arg, delay)

    # Chunk text to avoid exceeding the maximum command line length
    # (1024 characters)
    if delay is None:
        delay=self.android.internal.settings.INPUT_TEXT_DELAY_ON_DEVICE
    n=self.android.internal.settings.INPUT_TEXT_CHUNK_SIZE
    while arg != '':
        arglet=arg[:n]
	self.android.internal.transport.sh('CLASSPATH=/system/framework/input.jar app_process /system/bin com.android.commands.input.Input text "%s" "%s"' %
	(re.sub(r'([\\"$])', r'\\\1', arglet), delay ))
	time.sleep( min(self.android.internal.settings.INPUT_TEXT_DELAY_MAX,
		      max(self.android.internal.settings.INPUT_TEXT_DELAY_MIN,
                 	self.android.internal.settings.INPUT_TEXT_DELAY(len(arglet)))))
        arg=arg[n:]

android.internal.transport_generic._BRIEF_VIEW_SERVER_COMMANDS += ('FRAMEBUFFER',)

@hook(android.internal.transport_generic)
def sendevents(self, args):
	if getattr(self.internal.settings, 'LV_AVOID_SENDEVENT2',
				self.internal.device.google_experience):
		android.log.info(TAG, 'a.settings.LV_AVOID_SENDEVENT2=True. Falling back to sendevent')
	else:
		""" sendevent2 reduces the chance of timing errors """
		# Use a default delay of 20 ms; a delay of 0 causes drag failures on
		# Solana-Gingerbread
		delay=getattr(self.internal.settings, 'LV_SENDEVENT2_DELAY', 20)

		# Chunk to avoid exceeding the maximum command line length (1024):
		# (1024-len('sendevent2'))/len(' /dev/input/event0 000 000 000') == 33
		while args:
			if self.sh('sendevent2 ' + (' %d ' % delay).join(
					[ '%s %s %s %s' % tuple(args[n:n+4])
					for n in range(0,min(len(args),100),4) ])) != '':
				break
			args=args[100:]
		else:
			return

		android.log.info(TAG, 'sendevent2 failed. Falling back to sendevent')

	previous=sendevents.previous
	self.sendevents = lambda args: previous(self, args)
	return self.sendevents(args)

android.ui.dumpsys.DISPLAY_RE += [
		# Seen on recent tablet builds
		re.compile(r'Display: init=\d+x\d+ base=\d+x\d+ cur=(\d+)x(\d+) '),
                re.compile(r'Display: init=\d+x\d+ cur=(\d+)x(\d+) ') ]

nERROR_00n, ERROR_00n = encode('\nERROR 00\n'), encode('ERROR 00\n')
nERROR_0An, ERROR_0An = encode('\nERROR 0A\n'), encode('ERROR 0A\n')
nDONEn, DONEn = encode('\nDONE.\n'), encode('DONE.\n')
nDONEnDONEn, DONEnDONEn = encode('\nDONE.\nDONE\n'), encode('DONE.\nDONE\n')

@hook(android.ui.Screen)
def _DUMP(self):
	if getattr(self.android.settings, 'LV_AVOID_PTF_DUMP_COMMAND',
				self.android.internal.device.google_experience):
		return _DUMP.previous(self)

	def view_server_ptf_dump(command, timeout=None):
		def handler(command, data):
			# Special handling for PTF_DUMP errors, since they
			# neither close the socket nor end with 'DONE.\n'
			if (	data.endswith(nERROR_00n) or data == ERROR_00n or
					data.endswith(nERROR_0An) or data == ERROR_0An):
				raise socket.error('PTF_DUMP error')

			if data.endswith(nDONEn):
				""" Don't decode on Python 2.x because csv.DictReader doesn't
					accept unicode input. """
				return decode(data).split('\n')[:-2]

			# Termination string on some builds
			if data.endswith(nDONEnDONEn):
				return decode(data).split('\n')[:-3]

			if data in [ DONEn, DONEnDONEn ]:
				return []

			return None
		return self.android.internal.transport.view_server_generic(
				command, timeout, handler)

	# This is simpler, but much slower than the view server method.
	# id=android.ui.dumpsys(self.android).hash_for_title(self.title)

	# This is faster, but requires the caching code at the end of this method.
	id = 'ffffffff'			# Focus window
	if self.title is not None:
		w = self.android.ui._view_server_list_windows()
		try:
			id = [ hash for hash in w if w[hash] == self.title ][0]
		except IndexError:
			raise android.ui.ScreenNotFound(self.title)

	widgets=[]
	parents = { 0:None }

	def escape_crlf(s1):
		""" PTFDebugView escapes '\n' to '\\n', but not '\r'. The csv
			reader interprets '\\n' as 'n' and does not accept '\r' in
			the input. This function escapes \r and \n in the way the
			csv reader expects. """
		if '\\n' not in s1 and '\r' not in s1: return s1 # fast path
		s2=''
		escaped=False
		for c in s1:
			if not escaped and c == '\r':
				c = '\\\r'
			elif escaped and c == 'n':
				c = '\n'
			escaped = not escaped and c == '\\'
			s2 += c
		return s2

	dump = [	escape_crlf(_) for _ in
				view_server_ptf_dump('PTF_DUMP %s\n' % id) ]
                #view_server_ptf_dump('DUMP -1\n') ]

	class dump_csv_dialect(csv.Dialect):
		delimiter=','
		doublequote=False
		lineterminator='\n'
		escapechar='\\'
		quoting=csv.QUOTE_NONE

	regexp=re.compile('( *)(\S+) (?:id/|)(\S+)')
	for w in csv.DictReader(dump,
			('fullname', 'x', 'y', 'width', 'height', 'hasFocus',
			'isClickable', 'isEnabled', 'isFocused', 'isSelected',
			'AbsListView.count', 'AbsListView.selectedItemPosition',
			'isChecked', 'text', 'progress1', 'progress2',
			'drawables', 'hash'), dialect=dump_csv_dialect):
		if sys.version[0] == '2':
			w=dict((_, w[_].decode('utf-8')) for _ in w)
		level,w['type'],w['id']=regexp.match(w['fullname']).groups()
		w['level']=level=len(level)
		w['tag']=None

		w['isVisible'],w['isClipped']=True,False

		widget = android.ui.Widget(self.android, w)
		widgets.append(widget)

		parents[level+1] = widget
		if level > 0: parents[level]._add_child(widget)

	if self.title is None and len(widgets) > 0:
		w,h=widgets[0].right()+1,widgets[0].bottom()+1
		device = self.android.internal.device

		if not hasattr(device, 'cached_width'):
			device.cached_width, device.cached_height = 0, 0

		if (w,h) != (device.cached_width, device.cached_height):
			self.android.log.verbose(TAG,
				'rescanning dimensions: cur: %sx%s cached: %sx%s in: %sx%s' %
				(device.width, device.height,
				device.cached_width, device.cached_height, w, h))

			device.cached_width, device.cached_height = w, h

			android.ui.dumpsys(self.android)

	return dump, widgets



@hook(android.ui.UI)
def window(self):
	""" This is faster than the dumpsys method (20 ms vs 200 ms) """
	if getattr(self.android.settings, 'LV_AVOID_FOCUSED_COMMAND',
				self.android.internal.device.google_experience):
		return window.previous(self)

        def fallback_window_command():
            try:
                w=self.android.internal.transport.view_server_query( 'FOCUSED\n' )[0]
            except:
                w=""
            return w

        try:
            # can't use GET_FOCUS command in secure builds, so fall back to FOCUSED command
            if self.android.device.is_secure_build():
                raise Exception()
	    w=self.android.internal.transport.view_server_query('GET_FOCUS\n')[0].split()[1]
        except:
            w = fallback_window_command()

	self.android.log.verbose(android.ui.TAG, "Current window: '%s'" % w)
	return w

# XXX: make public for all devices?
@add_api(android.ui.Widget)
def is_checked(self):
	""" For checkboxes, returns True if checked, False otherwise.
		You may use the 'isChecked' widgetspec attribute to select widgets
		based on this attribute. """
	return self._Widget__w['isChecked'] == 'true'

@add_api(android.ui.Widget)
def drawables(self):
	""" Returns drawables reported by the widget.
		You may use the 'drawables' widgetspec attribute to select widgets
		based on this attribute. """
	return self._Widget__w['drawables']

for removed in [ 'APYTHON_LEGACY_ENCODING',
		'DEVICE_LEGACY_ANDROID_VERSION', 'DEVICE_LEGACY_INTERNAL_ID',
		'EXPERIMENTAL_ANR_SCREENSHOT_DIR', 'EXPERIMENTAL_FC_SCREENSHOT_DIR',
		'HOME_LEGACY_CLOSE_MODALS' ]:
	if hasattr(android.settings,removed):
		raise Exception('Deprecated setting %s detected. This feature is no longer supported.' % removed)

for renamed in [
		( 'LOG_LEVEL_FILE' , 'LOG_LEVEL_RUNTESTS_FILE' ),

		( 'EXPERIMENTAL_ADB_HANG_RECOVERY', 'INTERNAL_ADB_HANG_RECOVERY' ),
		( 'EXPERIMENTAL_ADB_HANG_RECOVERY_DELAY', 'INTERNAL_ADB_HANG_RECOVERY_DELAY' ),
		( 'EXPERIMENTAL_ADB_HANG_RECOVERY_TIMEOUT', 'INTERNAL_ADB_HANG_RECOVERY_TIMEOUT' ),

		( 'EXPERIMENTAL_RETRY_ON_CONNECTION_ERROR', 'INTERNAL_RETRY_ON_CONNECTION_ERROR' ),
		( 'EXPERIMENTAL_RETRY_ON_CONNECTION_ERROR_RETRIES', 'INTERNAL_RETRY_ON_CONNECTION_ERROR_RETRIES' ),
		( 'EXPERIMENTAL_RETRY_ON_CONNECTION_ERROR_DELAY', 'INTERNAL_RETRY_ON_CONNECTION_ERROR_DELAY' ),

		( 'EXPERIMENTAL_RETRY_ON_POSSIBLE_RESET', 'INTERNAL_RETRY_ON_CONNECTION_ERROR' ),
		( 'EXPERIMENTAL_RETRY_ON_POSSIBLE_RESET_RETRIES', 'INTERNAL_RETRY_ON_CONNECTION_ERROR_RETRIES' ),
		( 'EXPERIMENTAL_RETRY_ON_POSSIBLE_RESET_DELAY', 'INTERNAL_RETRY_ON_CONNECTION_ERROR_DELAY' ) ]:
	if hasattr(android.settings,renamed[0]):
		raise Exception('Deprecated setting %s detected. Please use %s instead.' % renamed)

@android.register_module_callback
def _(a):
	""" No longer check against ro.build.version.full since some Google
		Experience builds from LV are using it for upgrades.
		Similarly, ro.mot is being used by some tablets that lack
		LV view server extensions. """
	a.internal.device.google_experience = not getattr(a.internal.settings,
				'False',
				'charge_only_mode' in a.device.ls('/system/bin'))
	if a.internal.device.google_experience:
		android.log.info(TAG, 'Google Experience device detected')
		return

	""" Patches for home widgetspecs are placed here because a widgetspec
		with drawables can only be used on a device with LV extensions.
	"""


