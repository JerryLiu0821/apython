# -*- coding: utf-8 -*- 
#!/usr/bin/env python



# ./runtests.py --collect-only --generate-map
# ./runtests.py --run list

import android
import nose, nose.plugins
import linecache, os, pickle, re, sys, time, traceback
from xml.sax.saxutils import quoteattr


###############################################################################

TAG='runtests'

PLUGINS_DIRECTORY=os.path.join(
		os.path.dirname(sys.modules[__name__].__file__), 'plugins')

# XXX: filename: log_filename should get a description
# XXX: make public?
def log_screenshot(a, tag, base, caption, caption_html=None,
		caption_report=None):

	# XXX: Don't call log_filename until the screenshot is known to be
	# successful

    # Add exception handler for screenshot timeout exception
    try:
	    f=a.log.log_filename(
			'.'.join( [ base, a.settings.EXPERIMENTAL_LOG_SCREENSHOT_FORMAT ] ))
	    f2=android.log.strip_report_directory(f)
	    a.device.screenshot(f)
	    path=os.path.basename(f)
	    if not caption_html:
		    caption_html='<br />'.join(caption.splitlines())+'<br />'
	    a.log.error(tag, 'Screenshot saved to: %s: %s' % (f, caption),
			'<a href="%s"><img src="%s" /></a><br />%s' %
					(path, path, caption_html))

	    android.log.report(html='<a href="%s"><img src="%s" /></a><br />%s' %
			(f2, f2, caption_report if caption_report else
					(caption_html if caption_html else caption)))
    except:
        pass
    
def get_hostname():
    try:
        cmd2 = os.popen ('hostname')
        hostname = cmd2.readline()
        hostname = hostname.strip()
        cmd2.close()
    except:
        print 'Failed to get PC Name - Something is wierd\n'
    return hostname
   
def hook(c):
	def decorator(f):
		setattr(f, 'previous', getattr(c, f.__name__))
		setattr(c, f.__name__, f)
		return f
	return decorator

def unhook(c,name): setattr(c, name, getattr(c, name).previous)

connect_hooks = []

@hook(android)
def register_connect_hook(hook):
	""" PRIVATE """
	assert hook not in connect_hooks
	connect_hooks.append(hook)
	return hook

# Patch android.connect to add connect/disconnect hooks
@hook(android)
def connect(id=None,settings=[]):
	a=connect.previous(id,settings)
	# only call hooks if running from within a test
	if connected_devices is not None:
		for connect_hook in connect_hooks:
			connect_hook(a, True)
	return a

connected_devices = None

@android.register_connect_hook
def __strongref(a,connect):
	""" Manage an array of (strong) references to Android objects as they are
		created. This allows us to guarantee the lifetime of the objects so we
		can perform end-of-test actions on them in stopTest. """
	if connect:
		global connected_devices
		if connected_devices is None:
			if android.settings.EXPERIMENTAL_RUNTESTS_ALLOW_CONNECT_OUTSIDE_TESTS:
				return
			raise Exception(
"""Unexpected android.connect() call detected. Are you trying to connect() from
a file, module, or package level setUp() or tearDown() method? Doing so is
prohibited by default because it can cause unexpected test report results if
an Exception is raised.

You can allow calls to android.connect() from outside of test methods by
setting the setting EXPERIMENTAL_RUNTESTS_ALLOW_CONNECT_OUTSIDE_TESTS=True.
Connections made outside of test methods will NOT trigger connect hooks and
will NOT have logs enabled.

This setting only affects tests run through runtests.py.""")
		if a.device.id() in [ _.device.id() for _ in connected_devices ]:
			raise Exception('android.connect() called twice on the same device (id=%s) from the same test. You should never need to do this. Please reuse the original object instead.' % a.device.id())
		connected_devices.append(a)

@android.register_connect_hook
def __log_on_connect_hook(a,connect):

        try:
                # check if device is included in logging blacklist, if it is
                # return
                if( a.device.id() in 
                     [ _ for _ in android.settings.EXPERIMENTAL_DEVICE_LOGGING_BLACKLIST ]):
                        return
        except:
                pass

	if connect:
		a.internal.log_on_connect=[ a.internal.transport.popen(command,
					stdout=open(a.log.log_filename(template), 'wb+'))
			for command, template in a.settings.LOG_ON_RUNTESTS_CONNECT ]

		a.log.error('config', a.device.sh('getprop'))
	else:
		for p in a.internal.log_on_connect:
			android.internal.kill_process(p)
		del a.internal.log_on_connect

@android.ui.waitfor_hook
def __force_close_anr_screenshot(a, s):
	regexp=re.compile(a.settings.UI_DETECT_FORCE_CLOSE_TEXT)
	if (	s.widget(id='message', text=regexp) and
			s.widget(id='button1')):
		log_screenshot(a, TAG, 'screenshot-fc', 'Force close')

	regexp=re.compile(a.settings.UI_DETECT_ANR_TEXT)
	if (    s.widget(id='message', text=regexp) and
			s.widget(id='button1')):
		log_screenshot(a, TAG, 'screenshot-anr', 'ANR')

	return False

class XmlReportingPlugin(nose.plugins.Plugin):
	name = 'xml-reporting'

	def options(self, parser, env):
		nose.plugins.Plugin.options(self, parser, env)
		parser.add_option('--report-dir', action='store', dest='report_dir',
				default='report.%Y%m%d_%H%M%S',
				help=	"Output reports to this directory. You may use time.strftime formatting codes as documented at http://docs.python.org/library/time.html#time.strftime Default is report.YYMMDD_HHMMSS in the 'report parent directory'")
		parser.add_option('--report-parent-dir', action='store',
				dest='report_parent_dir',
				default='.',
				help=	"Output reports directory created in this directory. "
						"Default is the current directory.")

	def configure(self, options, conf):
		nose.plugins.Plugin.configure(self, options, conf)
		self.enabled = True

		self.passed = 0
		self.results = []
		self.tests_start = time.time()
		self.test_number = 0

		report_dir = os.path.join(options.report_parent_dir, get_hostname(),
				time.strftime(options.report_dir))

		@hook(android.log)
		def report_directory(): return report_dir

	def startTest(self, test):
		self.test_number += 1

		self.current={
				'address':test.address()[:(3 if test.address()[2] else 2)],
				'class':test.id(),
				'name':(test.shortDescription() or test.address()[0]),
				'start':time.time(),
				'result':None,
				'number':self.test_number,
				'logs':{},
				'report_texts':dict(html=[], xml=[])
		}

		try: os.makedirs(os.path.join(android.log.report_directory(), 'logs'))
		except: pass

		@hook(android.log)
		def logs_directory():
			return os.path.join('logs', '%05d' % self.test_number)

		@hook(android.log.Log)
		def log_filename(self_, template):
			assert '.' in template
			a=self_.android if self_ is not None else None
			id = None if a is None else a.device.id()
			f=os.path.join(android.log.logs_directory(), ('.%s%d.' % (
				'' if id is None else (id + '.'),
				len( [ k for k,v in self.current['logs'].setdefault(template,[])
						if k == id ] ) + 1)).join(template.rsplit('.',1)))
			self.current['logs'][template].append((id, f))
			path=os.path.join(android.log.report_directory(), f)

			try: os.mkdir(os.path.dirname(path))
			except OSError: pass

			type, format = template.rsplit('.',1)
			android.log.report(html=None,
					xml='        <%s format=%s id=%s src=%s />\n' % (type,
					quoteattr(format), quoteattr(str(id)), quoteattr(f)))

			return path

		@hook(android.log)
		def report(html=None, xml=None):
			if html: self.current['report_texts']['html'].append(html)
			if xml: self.current['report_texts']['xml'].append(xml)

		self.trace_log_txt = open(log_filename(None, 'trace_log.txt'), 'w')
		self.trace_log_html = open(log_filename(None, 'trace_log.html'), 'w')
		self.error_log_txt = open(log_filename(None, 'error_log.txt'), 'w')
		self.error_log_html = open(log_filename(None, 'error_log.html'), 'w')

		self.trace_log_txt.write('TRACE LOG FOR %s\n' % self.current['name'])
		self.error_log_txt.write('ERROR LOG FOR %s\n' % self.current['name'])

		HEADER="""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
</head>
<body>
<style>
.TAG_config { background: #0ff }
.TAG_exception { background: #f02 }
.TAG_trace { background: #eee }
.TAG_stability_exception { background: #ff6600 } 
.TAG_stability_debug { background: #ccff00 }
.TAG_stabexc { background: #ff6600 } 
.TAG_stabdeb { background: #ccff00 }
</style>
<h1>%s LOG FOR %s</h1>
<table><tr><th>Level</th><th>Tag</th><th>Message</th></tr>
""" % ('%s', self.current['name'])
		self.trace_log_html.write(HEADER % 'TRACE')
		self.error_log_html.write(HEADER % 'ERROR')

		MAP={
				android.settings.LOG_LEVEL_ERROR:'E',
				android.settings.LOG_LEVEL_WARNING:'W',
				android.settings.LOG_LEVEL_INFO:'I',
				android.settings.LOG_LEVEL_DEBUG:'D',
				android.settings.LOG_LEVEL_VERBOSE:'V',
				android.settings.LOG_LEVEL_VERYVERBOSE:'VV'
		}

		@hook(android.log)
		def _log(level, tag, message, html=None):
			if max(android.settings.LOG_LEVEL_RUNTESTS_FILE, android.settings.LOG_LEVEL_RUNTESTS_STDOUT) >= level:
				txt=('\n'.join( [ '[%d] %s [%s] %s' %
						(level, time.strftime('%Y-%m-%d %H:%M:%S'), tag, m)
						for m in message.splitlines() ]) + '\n').encode('utf-8')
				if html is None: html='<br>'.join(message.splitlines())
				html=('<tr class="LOG_LEVEL_%s TAG_%s"><td>%s</td><td>%s</td><td>%s</td></tr>\n' % (MAP[level], tag, MAP[level], tag, html)).encode('utf-8')
				if level <= android.settings.LOG_LEVEL_ERROR:
					self.error_log_txt.write(txt)
					self.error_log_html.write(html)
				if android.settings.LOG_LEVEL_RUNTESTS_FILE >= level:
					self.trace_log_txt.write(txt)
					self.trace_log_html.write(html)
				if android.settings.LOG_LEVEL_RUNTESTS_STDOUT >= level:
					print (txt[:-1])


		android.log.error('config', 'BUILDTIME: ' + android.BUILDTIME)
		android.log.error('config', ''.join(
				[ ('[%s]: [%s]\n' % (k, getattr(android.settings, k)))
						for k in dir(android.settings) if k.isupper() ] ))

		global connected_devices
		connected_devices = []

		sys.stdout.write('Running %s...' % self.current['name'])

	def stopTest(self, test):
		global connected_devices

		# Execute (dis)connect hooks
		for a in connected_devices:
			for connect_hook in connect_hooks:
				connect_hook(a, False)
		connected_devices = None

		unhook(android.log, '_log')
		unhook(android.log, 'report')
		unhook(android.log.Log, 'log_filename')
		unhook(android.log, 'logs_directory')

		self.trace_log_html.write('</table></body></html>')
		self.error_log_html.write('</table></body></html>')

		self.trace_log_txt.close()
		self.trace_log_html.close()
		self.error_log_txt.close()
		self.error_log_html.close()

		# record info
		self.current['end']=time.time()
		self.current['runtime']=self.current['end'] - self.current['start']

		self.results.append(self.current)

		del self.current

		# generate intermediate index file
		self.generate_index()

	def addSuccess(self, test):
		self.passed += 1
		print ('PASS')
		self.current['result'] = 'PASS'

	def addErrorOrFailure(self, test, err, type):
		TAG = 'exception'

		print (type)
		test_err = self.formatErr(err)
		html='\n'.join(test_err.splitlines())+'\n'

		android.log.error('test', test_err)
		android.log.report(html=html)

		if not hasattr(self,'current'):
			name=re.search("(module '.+') from ",
					test.shortDescription()).group(1)
			self.test_number += 1
			self.results.append({
					'address':name,
					'class':name,
					'name':name,
					'start':time.time(),
					'end':time.time(),
					'runtime':0.0,
					'result':type,
					'number':self.test_number,
					'logs':{},
					'report_texts':dict(html=[html], xml=[html])
			})
			return

		self.current['result'] = type
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
									'\n'
									'=============================\n'
									'== SCREEN WIDGETS\n'
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
						pass

	def addError(self, test, err): self.addErrorOrFailure(test, err, 'ERROR')

	def addFailure(self, test, err): self.addErrorOrFailure(test, err, 'FAIL')

	def finalize(self, result): self.generate_index(result)
	
	def getFailReasonfromTraceLog(self, path):
		reason = []
		lines = ''
		pattern = re.compile(r'(.*)raise\ self\.failureException\([\'\"](.*)[\'\"]\)')
		fp = open(path, "r")
		try:
			lines = fp.readlines()
			fp.close()
		except:
			pass
		msg = ''
		for line in lines:
			match = pattern.match(line.strip())
			if match :
				if msg == match.group(2):
					pass
				else:
					msg = match.group(2)
					reason.append(msg)
		return reason
	
	def getInfoFrmTraceLog(self, pattern, path):
		version = ''
		fp = open(path, "r")
		try:
			lines = fp.readlines()
			fp.close()
		except:
			pass
		for line in lines:
			match = pattern.match(line)
			if match :
				version = match.group(1)
		return version.strip()
	
	def generate_index(self, result=None):
		try: os.mkdir(android.log.report_directory())
		except: pass

		f = open(os.path.join(android.log.report_directory(), 'report.xml'), 'w')
		try:
			f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
			if result:
				f.write('<testsuite name="apython" tests="%d" errors="%d" failures="%d" time="%f">\n' % (result.testsRun, len(result.errors), len(result.failures), time.time() - self.tests_start))
			else:
				f.write('<testsuite name="apython" partial="true">\n')

			for r in self.results:
				f.write('    <testcase address=%s classname=%s name=%s description=%s time="%f" result=%s>\n' % (
						quoteattr(':'.join(r['address']) if r['address'][1] else r['address'][0]),
						quoteattr(r['class']),
						quoteattr(r['name'].split('|')[0].strip()),
						quoteattr(r['name'].split('|')[1].strip() if ('|' in r['name']) else r['name']),
						r['runtime'],
						quoteattr(r['result'])))
				f.write(''.join(r['report_texts']['xml']))
				f.write('    </testcase>\n')
			f.write('</testsuite>\n')
		finally:
			f.close()

		f = open(os.path.join(android.log.report_directory(), 'index.html'), 'w')
		def output(s):
			f.write(s + '\n')
			s = re.sub(r'<.*?>', '', s)
			if s != '' and result != None: print (s)
		try:
			if result:
				print ('Report directory: %s' % android.log.report_directory())
			output('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
			output('<pre>')
			"""output('=' * 60)
			output('TEST RESULTS' if result != None else 'PARTIAL TEST RESULTS')
			output('=' * 60)"""
			
			failNumber = -1
			errorNumber = -1
			if result:
				failNumber = len(result.failures)
				errorNumber = len(result.errors)
				"""output('Ran %d %s in %f seconds' % (result.testsRun,
						'tests' if result.testsRun > 0 else 'test',
						time.time() - self.tests_start))"""
				
				version_value = self.getInfoFrmTraceLog(re.compile(r'.*\[ro\.letv\.release\.date\].*\[(.*)\]'),os.path.join(android.log.report_directory(), 'logs/00001/trace_log.1.txt'))
				product_value = self.getInfoFrmTraceLog(re.compile(r'.*\[ro\.letv\.product\.name\].*\[(.*)\]'),os.path.join(android.log.report_directory(), 'logs/00001/trace_log.1.txt'))
				pass_value = self.passed
				fail_value = failNumber
				error_value = errorNumber
				all_value = result.testsRun
				
				case_rate = str(float('%.4f'%(float(all_value)/all_value))*100)+"%"
				pass_rate = str(float('%.4f'%(float(pass_value)/all_value))*100)+"%"
				fail_rate = str(float('%.4f'%(float(fail_value)/all_value))*100)+"%"
				error_rate = str(float('%.4f'%(float(error_value)/all_value))*100)+"%"
				
				##################################################
				#add a table for result
				output('<font size=12>自动测试结果：</font>')
				output('<font size=4>Version: %s dailybuild </font>'%version_value)
				output('<font size=4>Product: %s </font>'%product_value)
				output('<font size=4>Ip Addr: 10.58.48.104 </font>')
				output('<table width="600" border="1">')
				output('<tr bgcolor="#aa9f38">')
				output('<td>%-16s</b></td> <td>%-12s</td> <td>%-12s</td> <td>%-12s</td>' %('TEST CASE', 'PASSES', 'FAILURES', 'ERRORS'))
				output('</tr>')
				
				output('<tr bgcolor="#B0E0E6">')
				output('<td>%-16s</td> <td>%-12s</td> <td>%-12s</td> <td>%-12s</td>' %(all_value,pass_value,fail_value, error_value))
				output('</tr>')
				
				output('<tr bgcolor="#B0E0E6">')
				output('<td>%-16s</td> <td>%-12s</td> <td>%-12s</td> <td>%-12s</td>'%(case_rate,pass_rate,fail_rate,error_rate) )
				output('</tr>')
				output('</table>')
				output('')
				
				##################################################
				
				##################################################
				#add a table for change channel 
				output('<table width="600" border="1">')
				output('<tr>')
				output('<td>频道切换</td> <td>时长(阈值 1800ms)</td>')
				output('</tr>')
				for r in self.results:
					try:
						trace_log = r['logs']['trace_log.txt'][0][1]
						log_dir = os.path.dirname(r['logs']['error_log.txt'][0][1])
					except:
						trace_log = ''
						log_dir = ''
					rname = r['name'].split('|')[0].strip()
					if '详细时间' in rname:
						reason = self.getFailReasonfromTraceLog(os.path.join(android.log.report_directory(), trace_log))
						output('<tr>')
						output('<td>%s</td> <td> %s ms</td>' %(rname, reason[1].split(":")[1]))
						output('</tr>')
				output('</table>')
				##################################################
				
			if failNumber != -1 and failNumber != 0:
				output("FAIL: %d" %failNumber)
				output('<table width="600" border="1">')
				output('<tr>')
				output('<td>%5s</td> <td>%-55s</td> <td>%-10s</td> <td>%-6s</td>' % 
					('#####', 'TEST', 'RUN TIME', 'RESULT'))
				output('</tr>')
			
				for r in self.results:
					if r['result'] =='FAIL':
						try:
							trace_log = r['logs']['trace_log.txt'][0][1]
							log_dir = os.path.dirname(r['logs']['error_log.txt'][0][1])
						except:
							trace_log = ''
							log_dir = ''
					
						output('<tr>')
						output('<td>%05d</td> <td><a title="%s" href="%s">%-55.55s</a></td> <td>%-10f</td> <td><a href="%s">%s</a></td>' % 
							(r['number'],
							r['name'].split('|')[1].strip() if ('|' in r['name']) else r['name'],
							trace_log, r['name'].split('|')[0].strip(),
							r['runtime'], log_dir, r['result']))
						output('</tr>')
					# f.write(('<br clear=both />' + '-'*50 + '<br clear=both />').join(r['report_texts']['html']))
						output('<tr>')
						output('<td colspan="4">')
						allSteps = r['name'].split('|')[1].strip().split(';') if ('|' in r['name']) else r['name']
						if isinstance(allSteps, list):
							for steps in allSteps:
								f.write('<div>' + steps + '</div>')
						else:
							f.write('<div>' + allSteps + '</div>')
				
						reason = self.getFailReasonfromTraceLog(os.path.join(android.log.report_directory(), trace_log))
						if reason != []:
							for rs in reason:
								f.write('<div><font color="#FF0000">FAIL ----> ' + rs + '</font></div>')
						output('</td>')
						output('</tr>')
				output('</table>')
			
			if errorNumber != -1 and errorNumber != 0:
				output("ERROR: %d" %errorNumber)
				output('<table width="600" border="1">')
				output('<tr>')
				output('<td>%5s</td> <td>%-55s</td> <td>%-10s</td> <td>%-6s</td>' % 
					('#####', 'TEST', 'RUN TIME', 'RESULT'))
				output('</tr>')
			
				for r in self.results:
					if r['result'] =='ERROR':
						try:
							trace_log = r['logs']['trace_log.txt'][0][1]
							log_dir = os.path.dirname(r['logs']['error_log.txt'][0][1])
						except:
							trace_log = ''
							log_dir = ''
					
						output('<tr>')
						output('<td>%05d</td> <td><a title="%s" href="%s">%-55.55s</a></td> <td>%-10f</td> <td><a href="%s">%s</a></td>' % 
							(r['number'],
							r['name'].split('|')[1].strip() if ('|' in r['name']) else r['name'],
							trace_log, r['name'].split('|')[0].strip(),
							r['runtime'], log_dir, r['result']))
						output('</tr>')
					# f.write(('<br clear=both />' + '-'*50 + '<br clear=both />').join(r['report_texts']['html']))
						output('<tr>')
						output('<td colspan="4">')
						allSteps = r['name'].split('|')[1].strip().split(';') if ('|' in r['name']) else r['name']
						
						if isinstance(allSteps, list):
							for steps in allSteps:
								f.write('<div>' + steps + '</div>')
						else:
							f.write('<div>' + allSteps + '</div>')
				
						reason = self.getFailReasonfromTraceLog(os.path.join(android.log.report_directory(), trace_log))
						if reason != []:
							for rs in reason:
								f.write('<div><font color="#FF0000">ERROR ----> ' + rs + '</font></div>')
						output('</td>')
						output('</tr>')
				output('</table>')
			
			if self.passed != 0:
				output("PASS: %d" %self.passed)
				output('<table width="600" border="1">')
				output('<tr>')
				output('<td>%5s</td> <td>%-55s</td> <td>%-10s</td> <td>%-6s</td>' % 
					('#####', 'TEST', 'RUN TIME', 'RESULT'))
				output('</tr>')
			
				for r in self.results:
					if r['result'] =='PASS':
						try:
							trace_log = r['logs']['trace_log.txt'][0][1]
							log_dir = os.path.dirname(r['logs']['error_log.txt'][0][1])
						except:
							trace_log = ''
							log_dir = ''
					
						output('<tr>')
						output('<td>%05d</td> <td><a title="%s" href="%s">%-55.55s</a></td> <td>%-10f</td> <td><a href="%s">%s</a></td>' % 
							(r['number'],
							r['name'].split('|')[1].strip() if ('|' in r['name']) else r['name'],
							trace_log, r['name'].split('|')[0].strip(),
							r['runtime'], log_dir, r['result']))
						output('</tr>')
					# f.write(('<br clear=both />' + '-'*50 + '<br clear=both />').join(r['report_texts']['html']))
						output('<tr>')
						output('<td colspan="4">')
						allSteps = r['name'].split('|')[1].strip().split(';') if ('|' in r['name']) else r['name']
						for steps in allSteps:
							f.write('<div>' + steps + '</div>')
				
						reason = self.getFailReasonfromTraceLog(os.path.join(android.log.report_directory(), trace_log))
						if reason != []:
							for rs in reason:
								if reason.index(rs)==1:
									f.write('<div><font color="#00CD00">' + rs + '</font></div>')
								else:
									f.write('<div>' + rs + '</div>')
						output('</td>')
						output('</tr>')
				output('</table>')
	
			"""output('%5s %-55s %-10s %-6s' %
					('#####', 'TEST', 'RUN TIME', 'RESULT'))
			for r in self.results:
				try:
					trace_log = r['logs']['trace_log.txt'][0][1]
					log_dir = os.path.dirname(r['logs']['error_log.txt'][0][1])
				except:
					trace_log = ''
					log_dir = ''
				output('%05d <a title="%s" href="%s">%-55.55s</a> %-10f <a href="%s">%s</a>' %
						(r['number'],
						r['name'].split('|')[1].strip() if ('|' in r['name']) else r['name'],
						trace_log, r['name'].split('|')[0].strip(),
						r['runtime'], log_dir, r['result']))
				#f.write(('<br clear=both />' + '-'*50 + '<br clear=both />').join(r['report_texts']['html']))
				allSteps = r['name'].split('|')[1] if ('|' in r['name']) else r['name']
				all_Steps= allSteps.split(';')
				for steps in all_Steps:
					f.write(steps.strip()+'\n')
					
				reason = self.getFailReasonfromTraceLog(os.path.join(android.log.report_directory(),trace_log))
				if r['result'] == "FAIL":
					f.write("FAIL -----> " + reason + "\n")
				f.write(('<br clear=both />' + '-'*50 + '<br clear=both />'))"""
			output('</pre>')
		finally:
			f.close()

	def formatErr(self, err):
		exctype, value, tb = err
		return ''.join(traceback.format_exception(exctype, value, tb))

###############################################################################

class SerialPlugin(nose.plugins.Plugin):
	name = 'serial'

	def options(self, parser, env):
		nose.plugins.Plugin.options(self, parser, env)
		parser.add_option('--serial', action='store', dest='serial_number',
				default=None,
				help=	"Specify the serial number of the device to use "
						"as the default device for tests.")

	def configure(self, options, conf):
		nose.plugins.Plugin.configure(self, options, conf)
		if options.serial_number:
			os.environ['ANDROID_SERIAL'] = options.serial_number

class SettingsPlugin(nose.plugins.Plugin):
	name = 'settings'

	def options(self, parser, env):
		nose.plugins.Plugin.options(self, parser, env)
		parser.add_option('--settings', action='store', dest='settings',
				default=None,
				help=("'%s'-delimited list of apython settings files to use" %
						os.pathsep))

	def configure(self, options, conf):
		nose.plugins.Plugin.configure(self, options, conf)
		if options.settings is not None:
			for f in options.settings.split(os.pathsep):
				android.settings._load(android.settings, os.path.expanduser(f))

class TeePlugin(nose.plugins.Plugin):
	name = 'tee'

	def options(self, parser, env):
		nose.plugins.Plugin.options(self, parser, env)
		parser.add_option('--tee', action='store_true', dest='tee',
				default=False,
				help=	"Tee log output to console.")

	def configure(self, options, conf):
		nose.plugins.Plugin.configure(self, options, conf)
		if options.tee:
			android.settings.LOG_LEVEL_RUNTESTS_STDOUT=android.settings.LOG_LEVEL_RUNTESTS_FILE

class TracePlugin(nose.plugins.Plugin):
	name = 'trace'

	def options(self, parser, env):
		nose.plugins.Plugin.options(self, parser, env)
		parser.add_option('--disable-trace', action='store_false',
				dest='trace', default=True,
				help=	"disable trace plugin")
		parser.add_option('--trace-apython', action='store_true',
				dest='trace_apython', default=False,
				help=	"trace apython execution")
		parser.add_option('--trace-exclude', action='store',
				dest='trace_exclude', default=None,
				help=("'%s'-delimited list of paths that should not be traced" %
						os.pathsep))

	def configure(self, options, conf):
		nose.plugins.Plugin.configure(self, options, conf)
		if options.trace:
			self.enable_tracing(options.trace_apython, options.trace_exclude)

	def enable_tracing(self,trace_apython,trace_exclude):
		# ('<string>',1) is how CPython indicates native code execution
		EXCLUDE_LIST = ( sys.prefix, sys.exec_prefix, '<string>',
				sys.modules[__name__].__file__,
				'nose' + os.path.sep,
				'build' + os.path.sep + 'bdist'		# exclude eggs
		)

		for m in [ 'nose', 'PIL' ]:
			try:
				EXCLUDE_LIST += (__import__(m).__path__[0] + os.path.sep,)
			except ImportError:
				pass

		if not trace_apython:
			EXCLUDE_LIST += (
					android.__path__[0] + os.path.sep,
					# android.settings and android.log sometimes show up here.
					'android' + os.path.sep, # XXX: why does that happen?
					PLUGINS_DIRECTORY + os.path.sep )

		if trace_exclude:
			EXCLUDE_LIST += tuple([ os.path.abspath(_) for _ in
										trace_exclude.split(os.pathsep) ])

		def localtrace(frame, why, arg):
			if why == 'line':
				filename = frame.f_code.co_filename
				lineno = frame.f_lineno

				if (	not filename.startswith(EXCLUDE_LIST) and
						os.path.basename(filename) != 'runtests.py'):
					android.log.debug('trace',"%s(%d): %s" % (filename, lineno,
							linecache.getline(filename, lineno).rstrip()))

			return localtrace

		def globaltrace(frame, why, arg):
			if why == 'call':
				localtrace(frame, why, arg)
				return localtrace
			return None

		#sys.settrace(globaltrace)

###############################################################################

class TestLoader(nose.plugins.Plugin):
	name = 'loader'

	def options(self, parser, env):
		nose.plugins.Plugin.options(self, parser, env)
		parser.add_option('--map-file', action='store', dest='mapFile',
				default='tests.map', metavar='FILE',
				help=	"Store test mapping in this file. Default is the file "
						"tests.map in the current working directory.")
		parser.add_option('--generate-map', action='store_true', dest='generate_map',
				default=False, 
				help=	"Store test mapping in this file. Default is the file "
						"tests.map in the current working directory.")
		parser.add_option('--run', action='store', dest='runFiles',
				default=None, metavar='FILES',
				help=	"Run tests listed in the specified files (comma-"
						"separated list).")

	def configure(self, options, conf):
		nose.plugins.Plugin.configure(self, options, conf)
		self.enabled = True
		self.map = {}
		self.mapfile = os.path.expanduser(options.mapFile)
		self.generate = options.generate_map
		self.runfiles = None if options.runFiles is None else [
				os.path.expanduser(r) for r in options.runFiles.split(',') ]
		if self.generate is False:
			self.loadTestsFromNames = self._loadTestsFromNames
			try:
				f=open(self.mapfile, 'rb')
				d=pickle.load(f)
				if 'map' in d:
					self.map = d['map']
			except IOError:
				print ('Error reading %s' % self.mapfile)

	def finalize(self, result):
		""" Save new mapping file, if --generate-map was specified """
		if not self.generate:
			return
		f = open(self.mapfile, 'wb')
		pickle.dump({ 'map': self.map }, f)
		f.close()

	def _loadTestsFromNames(self, names, module=None):
		if self.runfiles is not None:
			if names == [ '.' ]:
				names = []
			for runfile in self.runfiles:
				f = open(runfile, 'r')
				try:
					names += [ l for l in [ _.strip() for _ in f.readlines() ]
									if l != '' and l[0] != '#' ]
				finally:
					f.close()

		return ( None, [ self.map.get(name, name) for name in names ] )

	def startTest(self, test):
		if self.generate:
			# ( file, module, class.method )
			address = test.address()
			description = test.shortDescription()
			if description != None:
				d = description.split('|')[0].strip()
				a = "%s:%s" % address[1:3]
				self.map[d] = a
				print ("%s ==> %s" % (a, d))

###############################################################################

def _exec(c, g, l): exec(c, g, l)

def logcat():
	#device_id = android.settings.DEVICES['TestDevice']['id']
        try:
            cmd1 = os.popen ('adb devices')
            device_ids = cmd1.readlines()[1:-1]
            if (len(device_ids)==1 and 'device' in str(device_ids) ):
                device_id = device_ids[0].split('\t')[0]
            cmd1.close()
        except:
            print 'Failed to get adb devices.\n' 
	a = android.connect(device_id)
	command = 'logcat -v threadtime'
	date =''.join (a.device.sh('date').split(' ')[-3].split(':'))
	mtime = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time()))
	filename = 'logcat_%s_%s_%s.txt'%(device_id,date,mtime)
      
	a.internal.log_on_connect=[ a.internal.transport.popen(command,
					stdout=open(a.log.log_filename(filename), 'wb+'))
							]
		

def main():
	#logcat()
	def is_plugin(c):
		try: return issubclass(c,nose.plugins.Plugin)
		except TypeError: return False

	plugins = [ ]

	def listdir(dir):
		try: return os.listdir(dir)
		except OSError: return []

	for p in [	os.path.join(PLUGINS_DIRECTORY,_)
				for _ in listdir(PLUGINS_DIRECTORY) if _.endswith('.py') ]:
		print ('Loading plugin %s' % p)

		l={}
		c=open(p,'rt').read()	# Windows or Unix line endings
		if hasattr(c,'decode'):
			c=c.decode('utf-8') # Python 2.x
		_exec(compile(c, p, 'exec'), globals(), l)

		plugins += [ c() for c in l.values() if is_plugin(c) ]

	plugins = [ c() for c in globals().values() if is_plugin(c) ] + plugins

	nose.main(argv=sys.argv + ['-s','-d'], config=nose.config.Config(
			plugins=nose.plugins.manager.DefaultPluginManager(plugins=plugins)))

if __name__ == '__main__':
	main()
